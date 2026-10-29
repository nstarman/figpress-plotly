# Contract: the built web page

```text
<name>/
├── index.html                 the figure, its controls, <meta name="figpress-plotly-version">
├── figure.json                {figure, groups, controls, page, fonts: {family: file}, neutrals}
├── fonts/<family>.ttf
└── vendor/plotly-<v>.min.js, figpress-plotly-<v>/index.js
<name>.html                    the same, everything inlined
```

Runtime (`index.js`, ES module): `mount(element, spec)` — loads fonts, draws at the container's
width, wires hover, groups, controls and theme, redraws on resize and theme change, keeping the
reader's state. Pure helpers exported for tests: `scaleLayout(layout, s)`, `applyState(spec,
state)`, `darkNeutral(color, palette)`.

Theme: `document.documentElement.dataset.theme` (`light`/`dark`), else `prefers-color-scheme`.
No request to another host, ever.
