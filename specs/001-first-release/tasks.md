# Tasks: First release of figpress-plotly

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Setup

- [x] T001 Add `LICENSE` (MIT), `.gitignore`, `README.md` (early development, link to the family
      site), `AGENTS.md`, `CHANGELOG.md`

## Phase 2: Foundational

- [x] T002 [P] `scripts/version.py` (as in figpress): tag → {pypi, npm}; `check`, `set`; tests

## Phase 3: User Story 1 — the name belongs to the family (P1)

- [x] T003 [P] [US1] Python package: `pyproject.toml`, `src/figpress_plotly/__init__.py`
      (`__version__`, docstring stating early development)
- [x] T004 [P] [US1] npm package: `package.json`, `index.js` (`export const version`)
- [x] T005 [US1] `tests/test_package.py`, `tests/package.test.mjs`: import and version

## Phase 4: User Story 2 — release by tagging (P1)

- [x] T006 [US2] `.github/workflows/release.yml` (as in figpress)
- [x] T007 [US2] `.github/workflows/ci.yml`: tests, both packages build, versions agree

## Phase 5: Polish

- [x] T008 Set `v2026.10.28`; run every check locally; show the maintainer before the repository
      is created and the tag pushed
