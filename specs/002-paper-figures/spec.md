# Feature Specification: Paper figures in print and on the web

**Feature Branch**: `002-paper-figures`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "The figpress-plotly library: a paper's figure is one `build(target)`
that gives the print PDF the paper publishes and a matching interactive web figure. Turn the
Paper Figure 7 spike (CP1, paper-stream-convexities-1) into the library: everything specified in
the paper's points; the paper's fonts in both outputs; the PDF printed at the exact page size; on
the web the same figure scaled to its column, with hover values and legend toggles on every
figure and controls that recompute what is plotted on a few; the reader's state kept across
redraws. Measure the match against the paper's existing figure. First use: one CP1 figure."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One definition, the paper's figure in print (Priority: P1)

An author writes a figure once, as a function of the target (`"pdf"` or `"web"`), giving sizes,
line widths, dash patterns, tick lengths and font sizes in points, as the paper does. Building it
for print gives the PDF the paper includes: the exact page size the author set, no added margin,
the paper's fonts embedded, mathematical labels in the paper's math fonts.

**Why this priority**: the PDF is the paper's figure (Principle I); nothing else matters if it is
not publishable.

**Independent Test**: build the example figure for print; the PDF's page is the requested size to
within 0.1 pt, every font it uses is embedded and is one of the fonts the author gave, and its text
and marks are where the definition puts them.

**Acceptance Scenarios**:

1. **Given** a figure defined in points with a page of W × H pt, **When** it is built for print,
   **Then** the PDF is one page of W × H pt with no margin, and lines, dashes, ticks and text have
   the sizes given in points.
2. **Given** the paper's font files, **When** the figure is built, **Then** the PDF embeds exactly
   those fonts and no fallback font.
3. **Given** a label with mathematics (italic symbols, upright text, sub- and superscripts), **When**
   it is built, **Then** it is set in the paper's math fonts in both outputs.

---

### User Story 2 - The same figure on the web, with hover and legend toggles (Priority: P1)

The author builds the same function for the web and gets a page that shows the figure exactly as
in print, scaled to the width of its column, with the paper's fonts. A reader hovers a curve to read
its values, and clicks a legend entry to hide or show that series and everything grouped with it
(for example a band, its edge and its line). Resizing the page keeps what the reader did.

**Why this priority**: the reason for the library; every figure gets these interactions.

**Independent Test**: open the example's web page at three widths; at each the figure overlays the
PDF (scaled) within the fidelity tolerance; hovering a curve shows its declared values; toggling a
legend entry hides its group; a resize keeps the toggles.

**Acceptance Scenarios**:

1. **Given** a built web figure, **When** it is shown in a column narrower or wider than the print
   width, **Then** everything (text, lines, dashes, ticks, margins) scales together and the layout
   is the print layout.
2. **Given** a series with declared hover values, **When** the reader points at it, **Then** those
   values are shown, formatted as declared.
3. **Given** a legend entry for a group, **When** the reader clicks it, **Then** every element of the
   group hides (and the entry dims); a second click shows them again.
4. **Given** hidden groups or moved controls, **When** the page is resized, **Then** the figure
   redraws with the reader's state unchanged.
5. **Given** a built web figure, **When** it is opened with no network, **Then** it works: nothing
   is loaded from another host, and a single self-contained HTML file is also produced.

---

### User Story 3 - Controls that recompute (Priority: P2)

For a few figures the author declares a control, such as a slider over a model parameter, and
how the plotted values depend on it. The reader moves the control and the figure shows the
result for that value; at the paper's value it is the paper's figure.

**Why this priority**: the most useful interaction, needed only on a few figures.

**Independent Test**: on the example, set the control to the paper's value and the figure equals
the print figure; move it and the affected series and labels change as declared, with hover values
following.

**Acceptance Scenarios**:

1. **Given** a control declared over a parameter, **When** the page loads, **Then** it sits at the
   paper's value and the figure is the paper's.
2. **Given** the reader moves the control, **When** the figure redraws, **Then** the declared
   series, shapes and labels show the values for the new setting, and nothing else moves.
3. **Given** a figure whose author wrote no browser code, **When** it is built with a control,
   **Then** the control works (figures declare interactions; they do not ship scripts).

---

### User Story 4 - Measured against the paper's existing figure (Priority: P2)

An author porting a figure from matplotlib compares the new PDF with the paper's current one: an
overlay image and a report of how far each element (frame, ticks, labels, legend) is from its
counterpart, against a stated tolerance.

**Why this priority**: matching is only real when it is measured (Principle II); porting the
paper's existing figures depends on it.

**Independent Test**: compare the example's PDF with its reference; the report lists each element's
offset and passes within 1 pt; a deliberately shifted element fails and is named.

**Acceptance Scenarios**:

1. **Given** a new PDF and a reference PDF of the same page size, **When** they are compared,
   **Then** an overlay image is written and each element's offset is reported in points.
2. **Given** an element outside the tolerance, **When** they are compared, **Then** the comparison
   fails and names it.

---

### User Story 5 - Light and dark (Priority: P3)

A reader whose site is in dark mode sees the figure in dark colours: background, text, axes and
grid follow the page's theme; the data's colours stay the paper's.

**Why this priority**: the website has light and dark themes; the print figure is unaffected.

**Independent Test**: show the example in a dark page; background, text and axes use the dark
theme, series colours are unchanged; switching the theme back restores the print colours.

**Acceptance Scenarios**:

1. **Given** a page in dark mode, **When** the figure is shown, **Then** its neutral colours
   (background, black and grey text, axes, grid) take the dark theme's and its data colours do not
   change.

### Edge Cases

- A column narrower than half the print width: the figure still scales as a whole (no reflow);
  below a minimum scale the page scrolls horizontally rather than overlapping text.
- A font file missing or unreadable: the build fails and names the font; it never falls back.
- A label wider than its place in print: the PDF is still produced; the comparison (US4) reports it.
- Log axes: shapes, annotations and hover values are placed by data value, as on linear axes.
- A legend toggle that hides every series: the axes, labels and legend stay.
- A control value outside its declared range (e.g. from a stale saved state): it is clamped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A figure MUST be one function of the target, `"pdf"` or `"web"`; both outputs come
  from it.
- **FR-002**: The library MUST let the author give every size in points (page, margins, frame,
  font sizes, line widths, dash patterns, tick lengths, marker sizes) and position marks and labels
  in page points or data values; it converts them for Plotly.
- **FR-003**: Dash patterns MUST be expressible as matplotlib's named styles scaled by line width
  (`:`, `--`, `-.`), as well as explicit lengths in points.
- **FR-004**: The author MUST be able to name the paper's font files (text and math); both outputs
  MUST use only those fonts, and a missing font MUST fail the build.
- **FR-005**: Labels MUST support the mathematics papers' figures use: italic and upright runs,
  subscripts, superscripts, Greek letters and simple fractions, set in the paper's fonts.
- **FR-006**: Print builds MUST give a one-page PDF at the exact page size, with no margin, fonts
  embedded.
- **FR-007**: Web builds MUST give a page (and a single self-contained HTML file) that loads no
  resource from another host, shows the print layout scaled to its container, and includes the
  paper's fonts.
- **FR-008**: Every web figure MUST support hover values (declared per series) and legend toggles
  (declared per group).
- **FR-009**: A figure MAY declare controls over parameters, with the values each affected series,
  shape and label takes for each setting; the shared runtime MUST apply them without per-figure
  scripts.
- **FR-010**: The reader's state (hidden groups, control values) MUST survive redraws and resizes.
- **FR-011**: The web figure MUST follow the page's light or dark theme for neutral colours only.
- **FR-012**: The library MUST provide a comparison of two PDFs of the same page: an overlay image
  and per-element offsets in points, failing beyond a given tolerance (default 1 pt).
- **FR-013**: The repository MUST include an example figure exercising every requirement above
  (bands, dashed and dotted lines, log axes, a drawn legend with toggles, a mathematical label,
  arrows, one control), built and checked in CI for both targets.
- **FR-014**: The browser runtime MUST be one package (`@nstarkman/figpress-plotly`) shared by every
  figure, vendored into each built page at its exact version.

### Key Entities

- **Figure**: the author's function of the target; returns the figure and what it declares (page
  size, fonts, hover, groups, controls).
- **Page geometry**: page size and frame in points; the units every other size is given in.
- **Font set**: the paper's font files, by role (text, bold, math italic, math upright).
- **Group**: elements that toggle together, with the legend entry that toggles them.
- **Control**: a parameter with its range, step and paper's value, and the values it gives the
  elements it affects.
- **Comparison**: two PDFs, their overlay and per-element offsets, a tolerance and a verdict.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The example's PDF matches its reference within 1 pt for every compared element (frame,
  tick labels, axis labels, legend, annotations), as the comparison reports.
- **SC-002**: At three column widths (half, equal to and twice the print width), the web figure
  overlays the scaled PDF within 1 pt (scaled).
- **SC-003**: One CP1 figure (Paper Figure 7) is ported: its PDF passes the comparison with the
  paper's current figure, and its web figure has hover, legend toggles and the η control.
- **SC-004**: A figure with a control is written with no browser code by its author.
- **SC-005**: Built web pages make no network request to another host (checked in CI).
- **SC-006**: Building the example for both targets takes under 30 seconds on CI.

## Assumptions

- Controls work from values computed in Python at build time for each setting of the control
  (a grid over its range), which the runtime swaps in; no science runs in the browser. A control
  with too many settings to precompute is out of scope for this feature.
- The PDF is produced through a headless browser (as in the spike); CI and authors have one
  available.
- matplotlib's DejaVu fonts serve the example; a paper with other fonts supplies its font files.
- Showing figpress-plotly figures in a paper's docs site (syw-site's `<Fig>`) is a later syw-site
  feature; this feature delivers the built page and single file it would embed.
- The example in this public repository is synthetic (its own formula and data); the CP1 port
  (SC-003) lives in the CP1 repository.
