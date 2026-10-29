# Implementation Plan: Paper figures in print and on the web

**Branch**: `002-paper-figures` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-paper-figures/spec.md`

## Summary

The library behind `build(target)`. An author writes a plain Plotly figure as a function of the
target and of the figure's parameters, in points, and decorates it with its page, an exact frame
(porting) or margins (a new figure), its fonts or a paper-wide style, and its controls.
figpress-plotly converts points to Plotly's px, sets labels with mathematics in the paper's fonts,
prints the PDF at the exact page through headless Chrome, and writes a web page (and a single file)
where one shared runtime scales the print layout, keeps the reader's state, and wires hover, group
toggles (a drawn legend or Plotly's own), precomputed controls and dark mode. A comparison tool
measures a PDF against the paper's figure when one is ported. Design decisions: [research.md](research.md).

## Technical Context

**Language/Version**: Python ≥ 3.11; ES2022 modules in the browser; Node ≥ 20 for tests

**Primary Dependencies**: plotly (7.x), kaleido (≥ 1; brings `choreographer`, which finds or
fetches Chrome), fonttools, pypdfium2, pillow. Browser: Plotly.js from the Python `plotly` package.

**Storage**: files (PDF, web page folder, single HTML)

**Testing**: pytest; `node --test`; Playwright (Chromium) smoke tests in CI

**Target Platform**: macOS and Linux with Chrome or Chromium; any modern browser for the pages

**Project Type**: library + CLI, with a browser runtime published to npm

**Performance Goals**: example builds both targets in < 30 s on CI (SC-006); a control setting
redraws in < 100 ms for Figure 7's size

**Constraints**: no network at page runtime (Principle V); fidelity within 1 pt (SC-001, SC-002);
no per-figure browser code (Principle IV)

**Scale/Scope**: figures of a paper (tens); a control's stored differences capped at 5 × 10⁶ numbers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan meets it |
|---|---|
| I. The paper is the reference | One decorated `build(target, **params)` per figure; both outputs come from it; the web page starts at the paper's parameter values. A paper style is defaults only (a template), so the figure stays the one definition. |
| II. Print fidelity in the paper's units | Every size in points through `fp.pt`, `fp.dash`, page coordinates; the paper's fonts registered in Kaleido's page and embedded in the PDF; PDF at the exact page with no margin; `fp.compare` measures it, in CI against a matplotlib reference (R9, R10). |
| III. The web adds, never changes | The runtime only scales, adds hover, toggles, controls and dark neutrals; control differences are found from the author's own builds, so nothing else can move (R5). |
| IV. One runtime, declared interactions | One `index.js`; groups, hover, controls are declared in Python; no per-figure scripts (R5–R7). |
| V. Pages that keep working | Plotly.js, the runtime and the fonts are vendored at pinned versions; a single self-contained file is written; CI checks no request leaves the page (R7, R10). |
| VI. Releases from tags | Unchanged: `release.yml` publishes PyPI and npm; the npm package now carries the runtime. |

Re-checked after Phase 1 design: passes; no deviations.

## Project Structure

### Documentation (this feature)

```text
specs/002-paper-figures/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/  python-api.md, cli.md, web-page.md
└── tasks.md   (/speckit-tasks)
```

### Source Code (repository root)

```text
src/figpress_plotly/
├── __init__.py        public API: figure, Control, Style, Fonts, dejavu, pt, dash, context, tex,
│                      text, stack, frac, legend, Entry, compare
├── units.py           pt → px, dash patterns, page/frame coordinates
├── fonts.py           Fonts, dejavu(), text widths (fontTools), @font-face and FontFace payloads
├── text.py            tex() subset → Plotly markup; stack(), frac()
├── legend.py          matplotlib-style drawn legend with group handles
├── figure.py          the decorator: page, frame or margins, fonts, style, controls; base layout
├── style.py           Style: a paper's fonts and print settings as a Plotly template (US6)
├── controls.py        builds each setting, finds the differing leaves, packs them
├── pdf.py             Kaleido SVG with the fonts → HTML with @page → Chrome print
├── web.py             page folder (index.html, figure.json, vendor/, fonts/) and single file
├── compare.py         render, overlay, text and frame offsets, verdict
├── cli.py             figpress-plotly build | compare
└── js/index.js        the runtime (also the npm package's entry)
examples/bands/
├── figure.py          the synthetic port (every requirement; FR-013)
└── reference.py       the same figure in matplotlib → reference.pdf (committed)
examples/native/
├── style.py           a paper's style (STIX, a Times-like face)
└── figure.py          a new figure: margins, the style, Plotly's legend, no reference (SC-007)
tests/                 test_*.py; runtime.test.mjs; smoke/ (Playwright)
```

`package.json` exports `./src/figpress_plotly/js/index.js`, so npm and PyPI ship one file. The
placeholder root `index.js` goes.

**Structure Decision**: a single library with one module per concern above; the runtime is one
file.

## Phases

1. **Print (US1)**: units, fonts, text, figure decorator, PDF. Checked with the example's PDF:
   page size, embedded fonts, compare against the reference.
2. **Compare (US4)**: needed to check phase 1 properly, so it lands with it.
3. **Web (US2)**: page writer, runtime (fonts, scaling, state, hover, legend toggles), single file,
   smoke tests including no-network and the three-width overlay.
4. **Native figures (US6)**, added during implementation: margins, `fp.Style`, Plotly's own legend
   as reader state, the native example (tasks T038–T042, numbered after the plan's).
5. **Controls (US3)**: difference finder, runtime application, control UI.
6. **Dark mode (US5)**: neutral mapping, theme detection.
7. **Release** `vYYYY.MM.DD` (PyPI and npm), then **port CP1's Paper Figure 7** in the CP1
   repository (SC-003) — outside this repository, after the release.

## Complexity Tracking

None.
