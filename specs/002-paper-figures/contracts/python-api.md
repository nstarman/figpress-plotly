# Contract: Python API (`import figpress_plotly as fp`)

```python
STYLE = fp.Style(fonts=fp.Fonts(text=..., bold=..., math_italic=..., math_upright=...), size=8, margins=(38, 6, 8, 28))

@fp.figure(page=(242, 170), style=STYLE,
           controls=[fp.Control("eta", 0.12, 0.68, 0.01, value=0.497, label=r"$\eta$")])
def rate(target, eta=0.497):
    ctx = fp.context()                      # the figure being built: page coordinates, fonts
    fig = go.Figure(...)                    # sizes through fp.pt(), fp.dash(":", 0.8)
    fp.text(fig, r"$\lambda$", 150, 5.6, 7)                    # baseline at a page point (pt)
    fp.text(fig, "Survey", np.log10(x), np.log10(y), 5.5, data=True, va="bottom", role="bold")
    fp.legend(fig, [fp.Entry("s1", r"1$\sigma$", band=..., edge=..., line=...)], at=(185.5, 4.5), size=7)
    return fig

rate.write_pdf("out/rate.pdf")
rate.write_web("out/rate/", single_file="out/rate.html")
fp.compare("out/rate.pdf", "paper/rate.pdf", tol=1.0, overlay="out/rate-overlay.png")  # -> Comparison
```

| Name | Does | Errors |
|---|---|---|
| `fp.figure(page, frame=None, margins=None, fonts=None, style=None, controls=(), name=None, spine=None)` | decorator; returns a `Figure` with `build`, `write_pdf`, `write_web`; the style's fonts, margins and spine unless given | frame and margins both; neither (nor a style); no fonts; bad geometry; a control not a parameter |
| `fp.Style(fonts, size=8, label=9, spine=0.7, ticks="inside", ticklen=3.5, tickwidth=0.6, minor_ticklen=2, line=1, marker=3, margins=(36, 6, 8, 30), color="black")` | a paper's style; `.template` | — |
| `fp.Control(name, lo, hi, step, value, label="", format=".2f")` | a slider over a parameter | `lo ≥ hi` or `step ≤ 0` |
| `fp.pt(v)` | points → px | — |
| `fp.dash(style, lw=1)` | `":"`, `"--"`, `"-."` scaled by `lw` pt, or a tuple of pt lengths → Plotly dash | unknown style |
| `fp.context()` | the figure being built: `x(pt)`, `y(pt)` page → paper coords, `width(text, role, size_pt)` | outside a build |
| `fp.Fonts(text, bold, math_italic, math_upright)`, `fp.dejavu(text="serif")` | font set; `dejavu()` takes matplotlib's DejaVu files | missing file (named) |
| `fp.tex(s)` | `$…$` mathematics → Plotly markup in the paper's fonts (italic/upright, Greek, `_`/`^`, `\rm`, symbols, binary-operator spacing; a script on the text before, `km s$^{-1}$`) | unsupported command (named); nested scripts; unbalanced braces |
| `fp.text(fig, s, x, y, size, role="text", color=, ha="left", va="baseline", data=False, dx=0, dy=0)` | a label aligned as matplotlib aligns text, at a page point (pt) or a data point (log10 on log axes) | outside a build |
| `fp.stack(fig, base, sup, sub, x, y, size, ...)` / `fp.frac(fig, num, den, x, y, size, ...)` | stacked scripts / a fraction, as separate labels | — |
| `fp.legend(fig, entries, at, size, title=None, ncol=1, handlelength=2, handleheight=0.7, handletextpad=0.8, columnspacing=2, labelspacing=0.5, borderpad=0.4, fill=, edgecolor=, linewidth=1, color=)` | a legend laid out as matplotlib's `loc="upper left"` at `at`; returns its box | — |
| `fp.Entry(group, label, line=None, band=None, edge=None)` | a legend entry and its handle | — |
| `Figure.write_pdf(path, **params)` | one-page PDF, exact page, fonts embedded | no Chrome (says how to get one); Chrome wrote no valid PDF |
| `Figure.write_web(dir, single_file=None, **params)` | page folder; optionally one HTML file | control structure differs (path named); over the size cap |
| `fp.compare(new, reference, tol=1.0, overlay=None)` | `Comparison`: `.ok`, `.elements`, `.report()` | page sizes differ |
