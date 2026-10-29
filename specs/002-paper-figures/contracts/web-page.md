# Contract: the built web page

```text
<name>/
├── index.html                 the figure and its controls; <meta name="figpress-plotly-version">
├── figure.json                {version, name, page, figure, fonts: {family: url}, controls: [...]}
├── fonts/<family>.ttf
└── vendor/plotly-<plotly.js version>.min.js, vendor/figpress-plotly-<version>/index.js
<name>.html                    the same in one file: Plotly.js, the runtime, the spec and the fonts (data URLs) inlined
```

`figure` is Plotly's JSON of the web figure at the paper's values; `controls` as in the data model.
The folder page fetches `figure.json`, so it is served; the single file also works from disk.

## Runtime (`index.js`, ES module; the npm package `@nstarkman/figpress-plotly`)

`mount(element, spec, {Plotly = globalThis.Plotly, palette = DARK})`: loads the fonts, then draws
the print layout scaled to the element's width (½× to 3× the print width; narrower, the element
scrolls) with whole-pixel geometry and exact glyph positions (`text-rendering: geometricPrecision`);
adds a `label.fp-control` slider with readout per control after the element; keeps the reader's
state across redraws (resize, theme change, control, legend click on the drawn legend or Plotly's
own); sets `element.dataset.theme` to `light` or `dark`. Returns `{state, draw}`.

Pure helpers, exported for tests: `scaleLayout(v, s)`, `roundGeometry(layout)`, `fitScale(width,
printWidth)`, `applyState(figure, state, controls)`, `setPath(obj, path, value)`, `traceGroup(t, i)`,
`formatValue(v, format)`, `darkNeutral(color, palette)`, `darken(v, palette)`, `darkLayout(layout,
palette)`, `isDark(document, window)`; constants `version`, `status`, `DARK` (the website's dark background
`#0B0E14` and text `#E5E9F0`).

Theme: a `?theme=dark|light` on the page, else `document.documentElement.dataset.theme`, else
`prefers-color-scheme`. No request to another host, ever.
