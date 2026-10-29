# Quickstart: check the feature end to end

```bash
uv sync
uv run python examples/bands/reference.py                       # the matplotlib reference (committed)
uv run figpress-plotly build examples/bands/figure.py:bands --out build/
uv run figpress-plotly compare build/bands.pdf examples/bands/reference.pdf --tol 1 --overlay build/overlay.png
uv run pytest && node --test "tests/*.test.mjs"
uv run pytest tests/smoke                                       # Playwright: hover, toggles, control, resize, offline, overlay at 3 widths
```

Expected: the comparison passes (every element within 1 pt); `build/bands/` opens offline and shows
the figure scaled to the window, hover values on the lines, legend entries that toggle their bands,
and a slider that recomputes the lines (at its starting value the figure is the PDF's).
