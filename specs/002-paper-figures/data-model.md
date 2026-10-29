# Data Model: Paper figures in print and on the web

## Figure (the decorated `build`)

| Field | Type | Rule |
|---|---|---|
| `build` | `(target: "pdf" \| "web", **params) -> go.Figure` | same structure for every parameter value (R5) |
| `page` | `(width_pt, height_pt)` | > 0 |
| `frame` | `(left, top, width, height)` in pt | inside the page |
| `fonts` | `Fonts` | every file readable; a missing one fails |
| `controls` | `list[Control]` | names are `build`'s keyword parameters |
| `name` | str | the output files' stem; default the function's name |

## Fonts

`text`, `bold`, `math_italic`, `math_upright`: paths to TTF/OTF files. Fixed family names
(`fp-text`, `fp-bold`, `fp-math-it`, `fp-math-rm`) are what figures and `tex()` use.

## Group

A name. Members: traces with `legendgroup == name`; shapes and annotations with
`meta == {"group": name}`. A legend entry carries the group it toggles.

## Control

| Field | Type | Rule |
|---|---|---|
| `name` | str | a keyword parameter of `build` |
| `lo`, `hi`, `step` | float | `lo < hi`, `step > 0`; settings `lo, lo+step, …, hi` |
| `value` | float | the paper's value; one of the settings (snapped, with a warning) |
| `label` | str | shown by the slider; may use `tex()` |
| `format` | str | d3 format for the readout, default `.2f` |

Packed for the page as `{name, label, format, settings: [...], index: i_paper, diffs: [{path,
values: [... per setting ...]}]}`, where `path` addresses a leaf of the figure JSON
(`["data", 3, "y"]`, `["layout", "shapes", 12, "y0"]`).

## Reader state (browser)

`{hidden: Set<group>, controls: {name: settingIndex}}`; applied on every draw; values out of range
are clamped.

## Comparison

`{tol_pt, elements: [{kind: "text" | "frame", name, dx_pt, dy_pt, ok}], overlay: path, ok}`; a
reference text with no counterpart is an element with `ok = false`.
