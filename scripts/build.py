"""Build the dependency-free GitHub Pages site from the editable diagram."""

from pathlib import Path
from html import escape
import json

from render import render


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Dysthe — Interactive Research Map"
family = json.loads((ROOT / "family.json").read_text())
repository_links = ' · '.join(
    f'<a href="https://github.com/matasvai/{escape(repo["name"])}">'
    f'{escape(repo["name"])}</a>' for repo in family['repositories']
)
document = render(ROOT / "source/research-map.html", title=TITLE)
document = document.replace(
    "<title>" + TITLE + "</title>",
    "<title>" + TITLE + "</title>\n"
    '<meta name="description" content="Explore the proposed optical Dysthe '
    'research programme: hybrid solvers, reduced models, DeepONet, active '
    'learning, validation, and routes to a scientific paper.">',
    1,
)
document = document.replace(
    "<body>\n<iframe",
    '<body>\n<style>body{max-width:1100px;margin-inline:auto;'
    'font-family:Arial,sans-serif}footer{margin-top:24px;padding-block:16px;'
    'border-top:1px solid currentColor;font-size:14px;line-height:1.5}'
    'footer a{color:inherit;text-underline-offset:3px}'
    '@media(min-width:768px){body{padding:32px}}</style>\n'
    '<main aria-label="Interactive Dysthe research map">\n'
    '<noscript>This interactive research map needs JavaScript enabled.</noscript>\n'
    '<iframe',
    1,
)
document = document.replace(
    "</iframe>\n<script>",
    '</iframe>\n</main>\n<footer>Optical Dysthe research · Proposed methods '
    'and evidence requirements. '
    '<a href="https://github.com/matasvai/dysthe-research-map">'
    'View the website source on GitHub</a>'
    '<p><strong>Research repositories</strong><br>' + repository_links + '</p>'
    '<p><a href="https://github.com/matasvai/dysthe-research-map/blob/main/FAMILY.md">'
    'Repository roles, branches, and workspace setup</a></p></footer>\n<script>',
    1,
)
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/index.html").write_text(document, encoding="utf-8")
(ROOT / "docs/.nojekyll").touch()
print("Built docs/index.html")
