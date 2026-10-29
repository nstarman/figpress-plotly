# AGENTS.md

figpress-plotly makes a paper's figures in Plotly so that one definition gives the print figure
(PDF) and a matching interactive web figure. Part of the figpress family. Read
`.specify/memory/constitution.md` first; it overrides this file.

## Layout

```
src/figpress_plotly/        the PyPI package (import figpress_plotly)
index.js                    the npm package (the web runtime, once it exists)
scripts/version.py          tag → PyPI and npm versions; check / set
tests/                      python -m unittest discover -s tests; node --test "tests/*.test.mjs"
.specify/, specs/           Spec Kit (v1.1.3): specify → plan → tasks → implement
```

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
