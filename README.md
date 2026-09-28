# Dysthe research map

An interactive guide to a proposed optical Dysthe research programme and how its
parts could support a scientific paper.

**Website:** https://matasvai.github.io/dysthe-research-map/

**Repository family:** [roles, branches, and migration order](FAMILY.md).
From this clone, `python3 scripts/workspace.py setup` prepares the four sibling
research repositories at the revisions recorded in `family.json`.

Six views connect the research question, reference simulations, candidate
learning methods, validation, and publication:

- Research map
- Hybrid solver
- Reduced model
- DeepONet
- Active learning
- Publication

These diagrams describe a research plan. They do not establish model performance,
physical discoveries, novelty, or publication readiness. Literature links are
included in each view.

## Edit and preview

The editable diagram is `source/research-map.html`. It contains the view content,
SVG layout, styles, and button interactions. The standalone runtime assets and
renderer are bundled so rebuilding does not require Codex or external packages.

With Python 3.10 or newer:

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000. Commit both source edits and the rebuilt
`docs/index.html` to update the deployed site.

## Hosting

GitHub Pages publishes `docs/` on the `main` branch. `.nojekyll` serves the
prebuilt static page. The page has no backend, analytics, remote fonts, or
JavaScript dependencies. It uses local browser storage to remember the selected
diagram; the diagram still works when storage is unavailable. Source links open
the cited publishers and papers in the same tab; use Back to return to the map.

The public repository contains only the website and its build files.
