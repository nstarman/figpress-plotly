# Contract: Python API (`import figpress_plotly as fp`)

```python
@fp.figure(page=(247, 207.4), frame=(32.2, 1.2, 207.1, 180.5), fonts=fp.dejavu(),
           controls=[fp.Control("eta", 0.12, 0.68, 0.01, value=0.497, label=fp.tex(r"$\eta$"))])
def rate(target, eta=0.497):
    ctx = fp.context()                      # the figure being built: page coordinates, fonts
    fig = go.Figure(...)                    # sizes through fp.pt(), fp.dash(":", 0.8)
    fig.add_annotation(x=ctx.x(150), y=ctx.y(5.6), text=fp.tex(r"$\lambda$"), ...)
    fp.legend(fig, [fp.Entry("s1", fp.tex("1$\sigma$"), band=..., line=...)], box=(185.5, 4.5, 236.5, 31))
    return fig

rate.write_pdf("out/rate.pdf")
rate.write_web("out/rate/", single_file="out/rate.html")
fp.compare("out/rate.pdf", "paper/rate.pdf", tol=1.0, overlay="out/rate-overlay.png")  # -> Comparison
```

| Name | Does | Errors |
|---|---|---|
| `fp.figure(page, frame, fonts, controls=(), name=None)` | decorator; returns a `Figure` with `build`, `write_pdf`, `write_web` | bad geometry; control name not a parameter |
| `fp.pt(v)` | points → px | — |
| `fp.dash(style, lw)` | `":"`, `"--"`, `"-."` scaled by `lw` pt, or a tuple of pt lengths → Plotly dash | unknown style |
| `fp.context()` | the figure being built: `x(pt)`, `y(pt)` page → paper coords, `text_width(s, role, size_pt)` | outside a build |
| `fp.Fonts(...)`, `fp.dejavu()` | font set | missing file |
| `fp.tex(s)` | LaTeX subset → Plotly markup in the paper's fonts | unsupported command (named) |
| `fp.stack(fig, base, sup, sub, x, y, size)` / `fp.frac(fig, num, den, x, y, size)` | stacked scripts / a fraction as annotations | — |
| `fp.legend(fig, entries, box, title=None)` | a drawn matplotlib-style legend; entries toggle groups on the web | — |
| `Figure.write_pdf(path)` | one-page PDF, exact page, fonts embedded | no Chrome (says how to get one) |
| `Figure.write_web(dir, single_file=None)` | page folder; optionally one HTML file | control structure differs (path named); over the size cap |
| `fp.compare(new, ref, tol=1.0, overlay=None)` | `Comparison`; `.ok`, `.report()` | page sizes differ |
