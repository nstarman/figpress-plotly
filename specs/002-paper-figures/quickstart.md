# Quickstart: check the feature end to end

```bash
uv sync
uv run python examples/bands/reference.py                       # the matplotlib reference (committed)
uv run figpress-plotly build examples/bands/figure.py:bands --out build/
uv run figpress-plotly compare build/bands.pdf examples/bands/reference.pdf --tol 1 --overlay build/overlay.png
uv run figpress-plotly build examples/native/figure.py:rotation --out build/   # a new figure: no reference
uv run pytest && node --test "tests/*.test.mjs"
uv run pytest -m smoke                                          # Playwright: hover, toggles, controls, resize, narrow, theme, offline, overlay at 3 widths
```

Expected: the comparison passes (every element within 1 pt); `build/bands/` opens offline and shows
the figure scaled to the window, hover values on the lines, legend entries that toggle their bands,
and a slider that recomputes the lines (at its starting value the figure is the PDF's).
`build/rotation.pdf` is one page of 242 × 170 pt with only the STIX fonts embedded; its web page's
Plotly legend hides a series on a click, kept across a resize. With `?theme=dark` either page's
neutral colours go dark and its data colours stay.
