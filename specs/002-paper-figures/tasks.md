# Tasks: Paper figures in print and on the web

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/)

**Tests**: required — Principle II ("fidelity is tested") and FR-013 (the example built and
checked in CI). Each story's tests come first and fail before its implementation.

## Format: `[ID] [P?] [Story] Description`

[P]: can run in parallel (different files, no dependency on an unfinished task).

## Phase 1: Setup

- [x] T001 `pyproject.toml`: dependencies plotly 7, kaleido ≥ 1, fonttools, pypdfium2, pillow;
      script `figpress-plotly = figpress_plotly.cli:main`; dev group pytest, playwright, matplotlib,
      numpy; package data `js/*.js`; `uv lock`
- [x] T002 `package.json`: export `./src/figpress_plotly/js/index.js`, `files` accordingly; delete
      the placeholder root `index.js`; update `tests/package.test.mjs`
- [x] T003 [P] CI (`.github/workflows/ci.yml`): `uv run pytest`, `node --test`, a `smoke` job
      (Playwright Chromium) and the example's build + compare; upload the example's outputs

## Phase 2: Foundational

- [x] T004 [P] Tests for units: `pt`, `dash` (`:`, `--`, `-.`, explicit, unknown style),
      page/frame → paper coordinates with the half-line inset, in `tests/test_units.py`
- [x] T005 [P] `src/figpress_plotly/units.py` (R2)
- [x] T006 [P] Tests for fonts: `dejavu()` files exist, a missing file fails naming it,
      `text_width` against fontTools, payloads (`@font-face` CSS, base64), in `tests/test_fonts.py`
- [x] T007 [P] `src/figpress_plotly/fonts.py` (R3)
- [x] T008 Tests for the decorator and context: geometry validation, control names must be
      parameters, `fp.context()` only inside a build, in `tests/test_figure.py`
- [x] T009 `src/figpress_plotly/figure.py`: `figure()`, `Figure`, `context()`; base layout from
      page and frame (size, margins, no automargin, fonts) (depends on T005, T007)

## Phase 3: User Story 1 — print (P1) 🎯 MVP

- [x] T010 [P] [US1] Tests for `tex`: italic/upright runs, `\rm`, Greek, `_`/`^`, symbols, an
      unsupported command names itself; `stack` and `frac` place annotations, in `tests/test_text.py`
- [x] T011 [P] [US1] `src/figpress_plotly/text.py` (R3)
- [x] T012 [P] [US1] Tests for `legend`: box, handles per kind, labels, group metadata, in
      `tests/test_legend.py`
- [x] T013 [P] [US1] `src/figpress_plotly/legend.py` (R6)
- [x] T014 [US1] Tests for the PDF: one page of exactly W × H pt (±0.1), only the given fonts
      embedded (pypdfium2), text where the definition puts it; no Chrome → a clear error, in
      `tests/test_pdf.py`
- [x] T015 [US1] `src/figpress_plotly/pdf.py` (R4) and `Figure.write_pdf`
- [x] T016 [US1] `examples/bands/reference.py` (matplotlib, synthetic: bands with dotted edges,
      lines, dashed survey lines with labels and arrows, a dash-dot vertical line with a stacked
      label, log axes with inward ticks and dotted grid, drawn legend, a band-definition inset with
      a fraction); commit `reference.pdf`
- [x] T017 [US1] `examples/bands/figure.py`: the same figure with figpress-plotly, one control (the
      band's ratio), hover on the lines, groups per band

## Phase 4: User Story 4 — compare (P2, lands with US1)

- [x] T018 [P] [US4] Tests for `compare`: identical PDFs pass; a label shifted by 2 pt fails and is
      named; a missing label fails; the frame's edges are found; different page sizes fail, in
      `tests/test_compare.py`
- [x] T019 [US4] `src/figpress_plotly/compare.py` (R9)
- [x] T020 [US4] `src/figpress_plotly/cli.py`: `build` and `compare` (contracts/cli.md), with tests
      in `tests/test_cli.py`
- [x] T021 [US1][US4] Example check: `examples/bands/figure.py` PDF vs `reference.pdf` within
      1 pt (SC-001), in `tests/test_example.py`; tune the example until it passes

## Phase 5: User Story 2 — the web, hover and toggles (P1)

- [x] T022 [P] [US2] Runtime tests (pure functions): `scaleLayout` (pixel keys, dashes, rounding of
      `ticklabelstandoff`), `applyState` (hidden groups on traces, shapes, annotations; legend
      entries dim), in `tests/runtime.test.mjs`
- [x] T023 [US2] `src/figpress_plotly/js/index.js`: `mount`, font loading, scaling to the
      container, state, hover, group toggles by event delegation on legend entries, resize (R7)
- [x] T024 [US2] Tests for the page writer: folder layout, `figure.json`, vendored Plotly and
      runtime at their versions, the single file has no external URL, in `tests/test_web.py`
- [x] T025 [US2] `src/figpress_plotly/web.py` and `Figure.write_web` (contracts/web-page.md)
- [x] T026 [US2] Smoke tests (Playwright, Chromium), `tests/smoke/test_browser.py` and `test_overlay.py`: hover shows the
      declared values; a legend click hides the group and dims the entry; resize keeps it; no
      request to another host; the page at ½×, 1× and 2× the print width overlays the scaled PDF
      within 1 pt (SC-002, SC-005)

## Phase 5b: User Story 6 — native figures (P1)

Added during implementation (after the plan), so its tasks are numbered after the plan's.

- [x] T038 [US6] `fp.figure`: `margins=` as an alternative to `frame=`; `fonts`, `spine` and margins
      default from a style; tests in `tests/test_figure.py`
- [x] T039 [US6] `fp.Style` (`src/figpress_plotly/style.py`): fonts, sizes, ticks, line widths and
      margins in pt, as a Plotly template the figure's own settings override; tests in
      `tests/test_style.py`
- [x] T040 [US6] Runtime: Plotly legend clicks become reader state (kept across redraws); runtime test
- [x] T041 [US6] `examples/native/figure.py`: a new figure in a Times-like font (STIX), with margins,
      the style, error bars, a band and Plotly's legend — no reference
- [x] T042 [US6] Tests: the native PDF (page, only the style's fonts, plot area from the margins) in
      `tests/test_native.py`; smoke: its legend click survives a resize

## Phase 6: User Story 3 — controls (P2)

- [x] T027 [P] [US3] Tests for the difference finder: only differing leaves are recorded, values
      per setting at 6 significant digits, structure change fails naming the path, the size cap,
      `value` snapped to a setting, in `tests/test_controls.py`
- [x] T028 [US3] `src/figpress_plotly/controls.py` (R5); `write_web` packs controls
- [x] T029 [US3] Runtime: a slider per control (label, readout), applies the setting's values,
      clamps a stale index; tests in `tests/runtime.test.mjs`
- [x] T030 [US3] Smoke: at the paper's value the page equals the PDF; moving the slider changes
      only the declared elements; hover follows; a resize keeps the setting

## Phase 7: User Story 5 — light and dark (P3)

- [x] T031 [P] [US5] Runtime tests for `darkNeutral`: greys invert into the palette, alpha kept,
      colours untouched
- [x] T032 [US5] Runtime: theme from `?theme=`, else `data-theme`, else `prefers-color-scheme`; redraw
      on change (R8)
- [x] T033 [US5] Smoke: dark page → neutral colours dark, data colours unchanged; back to light

## Phase 8: Polish and release

- [x] T034 [P] README (what it is, a short example, the CLI), AGENTS.md layout, CHANGELOG
      `## YYYY.MM.DD`
- [x] T035 Example build time < 30 s on CI (SC-006); a control redraw < 100 ms (smoke, measured)
- [x] T043 [US2] Edge case: below half the print width the figure keeps that size and its column
      scrolls (runtime `fitScale`; smoke `test_a_narrow_column_scrolls_rather_than_shrinking_past_half`)
- [ ] T036 Release `vYYYY.MM.DD` (`scripts/version.py set`, tag, `release.yml`); check fresh
      installs from PyPI and npm
- [ ] T037 Outside this repository: port CP1's Paper Figure 7 (SC-003) — the PDF passes
      `compare` with the paper's current figure; the web figure has hover, toggles and the η control

## Dependencies

Setup → Foundational → US1 (+ US4, whose compare checks US1) → US2 → US3 → US5 → Polish.
US2 needs US1's figure; US3 and US5 extend US2's runtime. Within a phase, [P] tasks run together.

## MVP

Phases 1–4: the library writes the paper's PDF and measures it against the reference.
