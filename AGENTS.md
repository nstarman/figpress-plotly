# AGENTS.md

figpress-plotly makes a paper's figures in Plotly so that one definition gives the print figure
(PDF) and a matching interactive web figure. Part of the figpress family. Read
`.specify/memory/constitution.md` first; it overrides this file.

## Layout

```
src/figpress_plotly/        the PyPI package (import figpress_plotly)
  figure.py                   @fp.figure: page, frame or margins, fonts, style, controls; build(target)
  units.py fonts.py style.py  points → px and dashes; the paper's fonts; fp.Style (a Plotly template)
  text.py legend.py           tex() and baseline-placed labels; a matplotlib-style drawn legend
  pdf.py web.py controls.py   the PDF (Kaleido SVG → Chrome print); the web page; control settings
  compare.py cli.py           PDF vs reference; figpress-plotly build | compare
  js/index.js                 the web runtime, and the npm package's entry (@nstarkman/figpress-plotly)
examples/bands/             a port: matched within 1 pt to its matplotlib reference (reference.py)
examples/native/            a new figure with a paper style, no reference
scripts/version.py          tag → PyPI and npm versions; check / set
tests/                      uv run pytest; node --test "tests/*.test.mjs"; uv run pytest -m smoke (browser)
.specify/, specs/           Spec Kit (v1.1.3): specify → plan → tasks → implement
```

Checks: the bands example's PDF must pass `figpress-plotly compare` against `reference.pdf` within
1 pt (`tests/test_example.py`); its web page must overlay its PDF at three widths
(`tests/smoke/test_overlay.py`). Regenerate `reference.pdf` only when the reference itself changes
(`uv run python examples/bands/reference.py`).

## Releasing

Versions are dates. A tag `vYYYY.MM.DD` (or `vYYYY.MM.DD.N`, N = 2, 3, … for another release the
same day) publishes PyPI `YYYY.MM.DD[.N]` and npm `YYYYMMDD.0.N` (N = 0 for the day's first):

```bash
python scripts/version.py set v2026.10.29     # writes src/figpress_plotly/__init__.py and package.json
git commit -am "Release v2026.10.29" && git tag v2026.10.29 && git push --follow-tags
```

`release.yml` checks the versions against the tag, builds, and publishes with trusted publishing
from the `pypi` and `npm` environments; a version already on an index is skipped. No token is
stored. npm's first release was published by hand (trusted publishing needs an existing package).
