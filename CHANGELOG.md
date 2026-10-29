# Changelog

Versions are dates: `vYYYY.MM.DD` (PyPI `YYYY.MM.DD`, npm `YYYYMMDD.0.0`), and `vYYYY.MM.DD.N` for
another release the same day.

## Unreleased

- numpy is a runtime dependency (it was imported but not declared, so a clean install failed).

The library (feature 002): a paper's figure as one `build(target)`.

- `@fp.figure(page, frame | margins, fonts | style, controls)`; sizes in points (`fp.pt`,
  `fp.dash`); `fp.Style`, a paper's fonts and print settings as a Plotly template.
- Text in the paper's fonts: `fp.tex()` (the LaTeX figures use), `fp.text()` (baseline-placed, at
  page or data points), `fp.stack()`, `fp.frac()`; `fp.legend()`, drawn as matplotlib draws one.
- `write_pdf()`: one page at exactly the given size, only the given fonts embedded.
- `write_web()`: the figure scaled to its column, with hover, legend toggles (drawn or Plotly's),
  controls (each setting built in Python), light and dark; a page folder and one self-contained
  HTML file, loading nothing from another host. The runtime is the npm package.
- `fp.compare()` and `figpress-plotly compare`: a PDF measured against a reference, text and frame.
- `figpress-plotly build`.

## 2026.10.28

First release: claims the name on PyPI and npm. No library code yet.
