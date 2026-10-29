# Data Model: Paper figures in print and on the web

## Figure (the decorated `build`)

| Field | Type | Rule |
|---|---|---|
| `build` | `(target: "pdf" \| "web", **params) -> go.Figure` | same structure for every control setting (R5) |
| `page` | `(width_pt, height_pt)` | > 0 |
| `frame` or `margins` | `(left, top, width, height)` / `(left, top, right, bottom)` in pt | one of the two, or the style's margins; the frame inside the page |
| `fonts` | `Fonts` | given or the style's; every file readable, a missing one fails |
| `style` | `Style` or none | applied as a Plotly template: the figure's own settings win |
| `spine` | pt | the frame's line width: given, the style's, or 0.7; Plotly's plot area is inset by half of it |
| `controls` | `list[Control]` | names are `build`'s keyword parameters |
| `name` | str | the output files' stem; default the function's name |

## Fonts

`text`, `bold`, `math_italic`, `math_upright`: paths to TTF/OTF files. Fixed family names
(`fp-text`, `fp-bold`, `fp-math-it`, `fp-math-rm`) are what figures, `tex()` and the pages use.

## Style

`fonts`, `size` (text and ticks), `label` (axis titles), `spine`, `ticks`, `ticklen`, `tickwidth`,
`minor_ticklen`, `line`, `marker`, `margins`, `color`, all lengths in pt. Its `template` is a
`go.layout.Template` (fonts, axes, backgrounds, legend, default scatter line and marker sizes).

## Group

What a legend entry toggles. Traces: their `legendgroup`, or `trace:<index>` for a trace without
one (so Plotly's own legend toggles it alone). A drawn legend's handle shapes and label carry
`name="legend:<group>"` (Plotly shapes have no `meta`); the label is what the reader clicks.

## Control

| Field | Type | Rule |
|---|---|---|
| `name` | str | a keyword parameter of `build` |
| `lo`, `hi`, `step` | float | `lo < hi`, `step > 0`; settings `lo, lo+step, …, hi` |
| `value` | float | the paper's value; snapped to the nearest setting, with a warning |
| `label` | str | shown by the slider; `tex()` markup |
| `format` | str | the readout: `.Nf`, else the value as is |

Packed for the page as `{name, label (Plotly markup), format, settings: [...], index: i_paper,
diffs: [{path, values: [one per setting]}]}`. `path` addresses a leaf of the figure JSON
(`["data", 3, "y"]`, `["layout", "annotations", 0, "text"]`). Float arrays are stored as float32
at 6 significant digits; at most 5 × 10⁶ stored numbers per page.

## Reader state (browser)

`{hidden: Set<group>, controls: {name: settingIndex}}`; applied on every draw (controls first,
then groups); an index out of range is clamped. A hidden group's traces are `visible: "legendonly"`
(Plotly keeps their legend entry, dimmed) and its drawn legend entry has opacity 0.35.

## Comparison

`{tol, elements: [{kind: "text" | "frame", name, dx, dy, ok}], overlay}` (pt); `ok` when every
element is within `tol`. A reference word with no counterpart in the new PDF is an element with
`ok = false`.
