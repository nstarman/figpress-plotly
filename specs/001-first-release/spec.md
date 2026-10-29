# Feature Specification: First release of figpress-plotly

**Feature Branch**: `001-first-release`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "figpress-plotly: paper figures in Plotly that give the print PDF and an
interactive web figure from one source. Start by claiming the name on PyPI and npm with a minimal,
honest first release and a tag-driven release workflow; the library itself is the next feature."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The name belongs to the family (Priority: P1)

Someone who installs `figpress-plotly` from PyPI or npm gets a genuine package from the figpress
family that says what figpress-plotly will be, that it is not usable yet, and where to follow it.

**Why this priority**: until a first release exists, anyone can take the names.

**Independent Test**: install from each index in a clean environment; importing (Python) or
requiring (npm) the package works and reports its version and status.

**Acceptance Scenarios**:

1. **Given** the first release, **When** someone installs `figpress-plotly` from PyPI and imports
   it, **Then** it imports, reports its version, and its description says it is in early
   development with a link to the family website.
2. **Given** the first release, **When** someone installs `@nstarkman/figpress-plotly` from npm and imports
   it, **Then** the same holds.

---

### User Story 2 - Release by tagging (Priority: P1)

The maintainer releases by pushing a date tag; the Python package goes to PyPI and the JavaScript
package to npm, with no stored token.

**Why this priority**: every later release of the library uses it.

**Independent Test**: push `vYYYY.MM.DD`; PyPI gets `YYYY.MM.DD` and npm `YYYYMMDD.0.0`, from that commit.

**Acceptance Scenarios**:

1. **Given** a pushed tag `vYYYY.MM.DD`, **When** the release workflow runs, **Then** PyPI gets
   `YYYY.MM.DD` and npm `YYYYMMDD.0.0`, both built from the tagged commit.
2. **Given** a tag that does not match the package versions, **When** the workflow runs, **Then**
   it fails before publishing anything.
3. **Given** a version already on an index (the hand-published first npm release), **When** the
   workflow runs, **Then** that index is skipped with a notice.

### Edge Cases

- Same-day second release `vYYYY.MM.DD.N`: PyPI `YYYY.MM.DD.N`, npm `YYYYMMDD.0.N`; each sorts after
  the day's first release.
- The Python and npm versions must always map to the same tag; CI fails when they do not.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain a Python package `figpress-plotly` (import name
  `figpress_plotly`) and a JavaScript package `@nstarkman/figpress-plotly` (npm, scoped as for the whole
  family), whose versions map to the same tag.
- **FR-002**: Both MUST state in their description that the library is in early development and
  link to the figpress website and the repository; neither may claim features it lacks.
- **FR-003**: Both MUST expose their version (`figpress_plotly.__version__`; `version` export).
- **FR-004**: Pushing `vYYYY.MM.DD` or `vYYYY.MM.DD.N` MUST publish both packages with trusted
  publishing from the tagged commit, and MUST fail before publishing if a version differs from the
  tag.
- **FR-005**: CI MUST check on every pull request that both packages build, install and import,
  and that their versions agree.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `pip install figpress-plotly` and `npm install @nstarkman/figpress-plotly` succeed from the first
  release on.
- **SC-002**: After the first npm release, a release needs only a pushed tag; no stored secret
  exists in the repository.

## Assumptions

- Repository `nstarman/figpress-plotly`, public, MIT licence.
- PyPI's pending trusted publisher is registered (workflow `release.yml`, environment `pypi`).
- The library itself (paper units, fonts, PDF printing, web runtime, declared interactions) is
  feature 002, specified separately from the design agreed so far.
