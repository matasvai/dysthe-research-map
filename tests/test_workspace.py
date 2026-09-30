import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workspace', ROOT/'scripts/workspace.py')
workspace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workspace)


class Workspace(unittest.TestCase):
    def test_existing_nonrepo_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            repo={'name':'dysthe-core'}
            destination=root/repo['name']
            destination.mkdir()
            sentinel=destination/'keep.txt'
            sentinel.write_text('existing user work')
            with self.assertRaisesRegex(ValueError,'left untouched'):
                workspace.setup_one(root,repo)
            self.assertEqual(sentinel.read_text(),'existing user work')

    def test_manifest_rejects_path_escape_and_foreign_origin(self):
        for name,url in [('../elsewhere','https://github.com/matasvai/dysthe-core.git'),
                         ('dysthe-core','https://example.com/other.git')]:
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'manifest.json'
                path.write_text(json.dumps({'schema_version':2,'scope':'water-wave-dysthe-spatial-v1','physical_system':'deep-water-gravity-waves','repositories':[{'name':name,'url':url,'revision':'a'*40}]}))
                with self.assertRaises(ValueError):
                    workspace.load_family(path)

    def test_real_manifest_has_four_repositories(self):
        self.assertEqual(len(workspace.load_family(ROOT/'family.json')['repositories']),4)

    def test_rejects_out_of_scope_family(self):
        family=json.loads((ROOT/'family.json').read_text())
        family['scope']='optical-dysthe-127-v1'
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'family.json'
            path.write_text(json.dumps(family))
            with self.assertRaisesRegex(ValueError, 'Scope violation'):
                workspace.load_family(path)
