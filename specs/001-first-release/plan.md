# Implementation Plan: First release of figpress-plotly

**Branch**: `001-first-release` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-first-release/spec.md`

## Summary

A Python package `figpress-plotly` (import `figpress_plotly`) and a JavaScript package
`figpress-plotly`, each exposing only its version and a description that says the library is in
early development, plus the same tag-driven release workflow as figpress. The library itself is
feature 002.

## Technical Context

**Language/Version**: Python ≥ 3.11; JavaScript (ES module, Node ≥ 18)

**Primary Dependencies**: none yet. Build: hatchling. CI: GitHub Actions
(`pypa/gh-action-pypi-publish`, `actions/setup-node` with Node 24)

**Storage**: N/A

**Testing**: `python -m unittest` (import, version, tag mapping); `node --test` (import, version)

**Target Platform**: PyPI; npm

**Project Type**: library (skeleton)

**Performance Goals**: N/A

**Constraints**: no runtime dependencies yet; no stored secrets

**Scale/Scope**: skeleton only

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| I–V (figures, fidelity, web, runtime, pages) | Not yet exercised: no figure code in this feature. The description says so (no claims of features it lacks). |
| VI. Releases from tags | `release.yml` on `v*` tags; `scripts/version.py` maps tag → PyPI and npm versions and fails on mismatch; OIDC from environments `pypi` and `npm`. |

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-first-release/
├── spec.md
├── plan.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml                    figpress-plotly (PyPI), hatchling
src/figpress_plotly/__init__.py   __version__
package.json                      figpress-plotly (npm): ES module, exports index.js
index.js                          export const version
scripts/version.py                tag → {pypi, npm}; `check`, `set` (same script as figpress)
tests/test_package.py, tests/package.test.mjs
.github/workflows/ci.yml, .github/workflows/release.yml
AGENTS.md, README.md, LICENSE, CHANGELOG.md
```

**Structure Decision**: both packages at the root for now; feature 002 decides where the runtime's
JavaScript lives once it has code.

## Complexity Tracking

None.
