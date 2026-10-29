# Research: Paper figures in print and on the web

Decisions for [plan.md](plan.md). Most come from the Paper Figure 7 spike (CP1), which matched the
paper's figure to about 1 pt in print and on the web.

## R1. How a figure is declared

- **Decision**: a decorator. The author writes `build(target, **params)` returning a
  `plotly.graph_objects.Figure`, decorated with the page geometry, fonts and controls:
  `@fp.figure(page=(247, 207.4), frame=(32.2, 1.2, 207.1, 180.5), fonts=fp.dejavu(), controls=[…])`.
  The decorated object writes both outputs (`.write_pdf()`, `.write_web()`) and is what the CLI loads
  (`module:name`).
- **Rationale**: the figure stays plain Plotly, which authors and agents know; the library adds
  only what Plotly lacks (units, fonts, print, runtime). One object per figure keeps the target and
  its declarations together (Principle I).
- **Alternatives**: a subclass of `go.Figure` (couples us to Plotly's internals); module-level
  constants read by convention (implicit, easy to get wrong).

## R2. Units

- **Decision**: helpers convert points to Plotly's CSS px (×4/3): `fp.pt(v)`; dash patterns
  `fp.dash(":", lw)` (matplotlib's scaled `:`, `--`, `-.`, or explicit lengths); page-point
  positions to Plotly paper coordinates `fig_ctx.x(pt)`, `fig_ctx.y(pt)`, from the frame. Plotly
  draws axis lines outside the plot area where matplotlib centres spines on it, so the frame is
  inset by half a line width (as the spike measured).
- **Rationale**: the paper's unit everywhere (Principle II); the conversions the spike needed, and
  no more.
- **Alternatives**: setting Plotly's DPI (no such setting: Plotly is in CSS px).

## R3. Fonts and mathematics

- **Decision**: `fp.Fonts(text=, bold=, math_italic=, math_upright=)` of font files (`fp.dejavu()`
  gives matplotlib's DejaVu set, the fonts of most matplotlib papers). Each gets a fixed family name.
  Labels with mathematics use `fp.tex(r"$\lambda_{\rm C}$ …")`, a small converter from the LaTeX
  subset figures use (italic letters, `\rm`/`\mathrm`, Greek, `_`, `^`, `\in` and similar symbols) to
  Plotly's text markup (`<span style="font-family:…">`, `<sub>`, `<sup>`). A stacked sub- and
  superscript (`\lambda^{\rm sim}_{\rm C}`) and a fraction are placed as separate annotations by
  `fp.stack()` and `fp.frac()`, as the spike did (Plotly cannot stack them). Text width for
  layout comes from the font file (fontTools advance widths).
- **Rationale**: MathJax in Plotly does not use the paper's fonts and cannot be printed through
  Kaleido's SVG faithfully; the subset is what figures use.
- **Alternatives**: MathJax (wrong fonts); pre-rendered SVG glyphs (not selectable, hard to place).

## R4. The PDF

- **Decision**: Kaleido (≥ 1) writes the figure as SVG, with the fonts registered in its page as
  binary `FontFace`s before Plotly measures text; the SVG is wrapped in an HTML page with the same
  `@font-face`s and `@page { size: W pt H pt; margin: 0 }` and printed by the same headless
  Chrome Kaleido uses (`choreographer`'s browser path), which embeds subsets of the fonts.
- **Rationale**: Kaleido's own PDF adds a margin and cannot use page fonts (found in the spike);
  printing the SVG gives the exact page and real embedded fonts.
- **Alternatives**: Kaleido PDF (margin, fallback fonts); svglib/cairosvg (no web fonts, different
  text layout from the browser that draws the web figure).

## R5. Controls: precomputed, found by difference

- **Decision**: a control is `fp.Control(name, lo, hi, step, value=…, label=…)`. At build time the
  library calls `build("web", **{name: v})` for every setting and compares each result with the
  figure at the paper's value: every leaf that differs (a trace's `y`, a shape's `y0`, an
  annotation's `text`, a hover template) is recorded with its values per setting. The page holds
  the paper's figure plus these differences; the runtime applies the setting's values. Different
  structure between settings (another number of traces, a new shape) fails the build with the path
  that differs. Numbers are stored at 6 significant digits.
- **Rationale**: the maintainer chose precomputed controls; finding the differences means the author
  declares only the parameter, writes no browser code (FR-009, SC-004), and nothing else can move
  (US3 scenario 2).
- **Alternatives**: the author lists the affected elements (more to write, easy to miss one); a
  browser function (rejected: Principle IV and the maintainer's choice). Size: Figure 7's η control
  (57 settings × 4 lines × 800 points) is about 1.5 MB as JSON before compression; acceptable, and
  the plan caps a build at 5 × 10⁶ stored numbers with a clear error.

## R6. Legends and groups

- **Decision**: groups are Plotly's `legendgroup` on traces, and a `group` name in `meta` on shapes
  and annotations. Legends are drawn, as matplotlib draws them, by `fp.legend(entries, box=…)`:
  a rounded box, a handle per entry (line, band, band with edge and line, marker) and its label,
  in page points. On the web, clicking an entry's label or handle toggles its group; the entry dims.
- **Rationale**: Plotly's legend cannot match a matplotlib legend's layout; a drawn one matches
  and is still interactive (the spike's approach).
- **Alternatives**: Plotly's legend restyled (cannot place handles and labels as matplotlib does).

## R7. The web runtime

- **Decision**: one ES module, `index.js` (the npm package `@nstarkman/figpress-plotly` and, the
  same file, vendored by the Python package). It loads the fonts (`FontFace` from the page's font
  files), waits for them, scales every pixel-valued layout key and dash pattern to the container
  (CSS zoom or transforms break Plotly's hover), keeps the reader's state (hidden groups, control
  values) and re-applies it on every draw, wires group toggles and controls (an `<input type=range>`
  per control under the figure), and maps neutral colours for dark mode. Plotly.js is the build
  that ships with the Python `plotly` package used to build the figure (`get_plotlyjs()`), so the
  figure JSON and the renderer always match.
- **Rationale**: Principle IV (one tested runtime), Principle V (pinned, vendored).
- **Alternatives**: `plotly.io.to_html` (CDN by default; no fonts, scaling or state); a framework
  (unneeded).

## R8. Dark mode

- **Decision**: neutral colours are greys (r = g = b, any alpha) including black and white; in dark
  mode the runtime maps each grey level L to 1 − L, scaled into the website's dark palette (its
  background and text colours), and leaves every other colour alone. The theme is the document's
  `data-theme` (`light`/`dark`, as the website sets it) or else `prefers-color-scheme`, and the
  figure redraws when either changes. A page embedded in another (an iframe) follows the parent
  when the parent passes the theme (a `?theme=` parameter or a message); that wiring belongs to the
  embedding site.
- **Rationale**: FR-011: neutral colours only, data untouched; the website's own convention.

## R9. Comparing with the paper's figure

- **Decision**: `fp.compare(new.pdf, reference.pdf, tol=1.0)` (and the CLI): both rendered with
  pypdfium2 at 600 dpi; an overlay image (reference in red, new in cyan); text elements extracted
  from both PDFs with their boxes and matched by content (tick labels, axis labels, legend labels,
  annotations), each offset reported in points; the frame found from long horizontal and vertical
  runs of dark pixels and its four edges compared. It fails beyond `tol`, naming each element.
- **Rationale**: Principle II's "overlay and per-element bounding boxes"; text is most of a
  figure's elements and the frame anchors the rest. The spike's checks were these, by hand.
- **Alternatives**: whole-image difference metrics (no element is named; a 1 pt shift of a label
  barely moves a global metric).

## R10. Testing

- **Decision**: pytest (units, `tex`, legends, control differences, page geometry, embedded fonts,
  compare); `node --test` (runtime: scaling, state, controls, theme mapping, as pure functions);
  Playwright smoke tests in CI on Chromium (hover, toggle, control, resize keeps state, no request
  to another host, overlay with the PDF at three widths). The example's reference PDF is made by
  a matplotlib script in the repository, so the fidelity test is a real port.
- **Rationale**: Principle II "fidelity is tested"; as figpress-apps tests its runtime.
