"""Clone the pinned research family safely; never reset existing checkouts."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

HUB = Path(__file__).resolve().parents[1]


def git(folder, *args):
    return subprocess.check_output(['git', '-C', str(folder), *args], text=True).strip()


def load_family(path):
    family = json.loads(path.read_text())
    if family.get('schema_version') != 2 or family.get('scope') != 'water-wave-dysthe-spatial-v1' or family.get('physical_system') != 'deep-water-gravity-waves':
        raise ValueError('Scope violation: workspace must target the approved water-wave model')
    names = set()
    for repo in family['repositories']:
        name = repo['name']
        if not re.fullmatch(r'dysthe-[a-z-]+', name) or name in names:
            raise ValueError('Repository names must be unique Dysthe directory names')
        if repo['url'] != f'https://github.com/matasvai/{name}.git':
            raise ValueError(f'Unexpected repository URL for {name}')
        if not re.fullmatch(r'[0-9a-f]{40}', repo['revision']):
            raise ValueError(f'Missing immutable revision for {name}')
        names.add(name)
    return family


def inspect_existing(path, repo):
    if not (path / '.git').is_dir():
        raise ValueError(f'{path} exists but is not a standalone clone; left untouched')
    remote = git(path, 'remote', 'get-url', 'origin')
    if remote != repo['url']:
        raise ValueError(f'{path} has a different origin; left untouched')
    revision = git(path, 'rev-parse', 'HEAD')
    dirty = bool(git(path, 'status', '--porcelain'))
    status = 'PINNED' if revision == repo['revision'] and not dirty else 'DIFFERS FROM PIN'
    print(f"{repo['name']}: {status} ({revision[:12]})")


def setup_one(root, repo):
    destination = root / repo['name']
    if destination.exists() or destination.is_symlink():
        inspect_existing(destination, repo)
        return
    with tempfile.TemporaryDirectory(prefix='.dysthe-clone-', dir=root) as stage:
        clone = Path(stage) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', repo['url'], str(clone)], check=True)
        # This is a brand-new checkout only. Existing directories are never reset.
        subprocess.run(['git', '-C', str(clone), 'checkout', '--quiet', '-B', 'main', repo['revision']], check=True)
        subprocess.run(['git', '-C', str(clone), 'branch', '--set-upstream-to=origin/main', 'main'], check=True, stdout=subprocess.DEVNULL)
        if destination.exists() or destination.is_symlink():
            raise ValueError(f'{destination} appeared during clone; refusing to replace it')
        clone.rename(destination)
    inspect_existing(destination, repo)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['setup', 'status'])
    parser.add_argument('--root', type=Path, default=HUB.parent, help='Parent directory for sibling research clones')
    args = parser.parse_args()
    try:
        family = load_family(HUB / 'family.json')
        root = args.root.expanduser().resolve()
        if args.command == 'setup':
            root.mkdir(parents=True, exist_ok=True)
        for repo in family['repositories']:
            path = root / repo['name']
            if args.command == 'setup':
                setup_one(root, repo)
            elif path.exists():
                inspect_existing(path, repo)
            else:
                print(f"{repo['name']}: NOT CLONED")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Workspace setup stopped: {error}\n')


if __name__ == '__main__':
    main()
