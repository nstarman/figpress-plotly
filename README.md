# figpress-plotly

A paper's figures in Plotly: one definition gives the print figure the paper publishes (PDF) and
a matching interactive web figure that can do more — hover values, legend toggles, controls that
recompute what is plotted, light and dark — while never disagreeing with the paper.

Part of the [figpress](https://nstarkman.space/figpress/) family. In early development: the API
may still change between releases.

```bash
pip install figpress-plotly       # needs Chrome or Chromium to print PDFs (Kaleido's)
```

## A figure

A figure is plain Plotly, written once as a function of the target (`"pdf"` or `"web"`), with
every size in points:

```python
import figpress_plotly as fp
import plotly.graph_objects as go

# The paper's style, once for all its figures: fonts (any TTF/OTF files) and print settings in pt.
STYLE = fp.Style(fonts=fp.Fonts(text="STIXGeneral.ttf", bold="STIXGeneralBol.ttf",
                                math_italic="STIXGeneralItalic.ttf", math_upright="STIXGeneral.ttf"),
                 size=8, margins=(38, 6, 8, 28))

@fp.figure(page=(242, 170), style=STYLE)          # one column; the plot area is the page less the margins
def rotation(target):
    fig = go.Figure(go.Scatter(x=r, y=v, name="Model", hovertemplate="%{y:.0f} km/s"))
    fig.update_yaxes(title_text=fp.tex(r"$v_{\rm c}$ (km s$^{-1}$)"))
    fig.update_layout(hovermode="closest" if target == "web" else False)
    return fig

rotation.write_pdf("src/tex/figures/rotation.pdf")              # the paper's figure
rotation.write_web("site/rotation/", single_file="rotation.html") # its web figure
```

- **The PDF** is one page of exactly the size given, with only the style's fonts embedded:
  `\includegraphics` it like any other figure (in a showyourwork paper, it is the script's output).
- **The web figure** is the same layout scaled to its column: a folder (page, figure data, fonts,
  and Plotly.js and the runtime at pinned versions) and one self-contained HTML file. Nothing is
  loaded from another host.
- **The style** is a Plotly template: whatever a figure sets itself wins. Give `margins=` or an
  exact `frame=` (left, top, width, height) in pt.
- **Text**: `fp.tex()` sets the mathematics figures use (`$\lambda_{\rm C}$`, Greek, sub- and
  superscripts, `\in`, `\times`, `km s$^{-1}$`) in the paper's fonts; `fp.text()` places a label by
  its baseline at a page or data point; `fp.stack()` and `fp.frac()` for stacked scripts and
  fractions.
- **Legends**: Plotly's own, or `fp.legend()`, drawn as matplotlib draws one. On the web, clicking an
  entry hides its series (and everything in its `legendgroup`); the reader's choices survive
  resizing.

See [`examples/native/`](examples/native/).

## Controls

A parameter of the figure can become a slider on the web:

```python
@fp.figure(page=..., style=STYLE, controls=[fp.Control("r", 0.12, 0.68, 0.02, value=0.50, label="$r$")])
def bands(target, r=0.50):
    ...  # draw with r
```

Every setting is built in Python when the page is written, and only what differs from the paper's
figure is stored; the page swaps those values in. No science runs in the browser, and at the
paper's value the figure is the paper's. A figure whose traces, shapes or labels appear or
disappear with the setting is refused (values may change, structure may not).

## Light and dark

On the web, greys (black and white included) follow the theme — the website's dark palette — and
every other colour stays the paper's. The theme is a `?theme=dark|light` on the page (how an
embedding site passes its own), else the page's `data-theme`, else the system's.

## Porting a matplotlib figure

When a figure already in the paper is moved to figpress-plotly, measure the new PDF against it:

```bash
figpress-plotly compare new.pdf paper-figure.pdf --tol 1 --overlay overlay.png
```

It matches every piece of text by content and the axes frame from the image, reports each offset
in points, and writes an overlay. `fp.dejavu()` gives matplotlib's DejaVu fonts; `fp.dash(":")`
and `fp.legend()` follow matplotlib's dash patterns and legend layout. See
[`examples/bands/`](examples/bands/): it matches its matplotlib reference within 1 pt.

## Command line

```bash
figpress-plotly build figures.py:rotation --out build/           # rotation.pdf, rotation/, rotation.html
figpress-plotly build figures.py:rotation --out build/ --target pdf
figpress-plotly compare build/rotation.pdf reference.pdf --tol 1 --overlay overlay.png
```

## Limits

- `fp.tex()` covers the LaTeX figures use, not all of LaTeX; an unsupported command is named.
- With several controls, each is built with the others at the paper's values: moving two at once
  is right when their effects are independent.
- On screen, at half the print width a pixel is 1.5 pt; browsers draw hairlines on whole pixels.
- Ported figures: text widths are unkerned (a long title can be ~0.35 pt wide), and matplotlib's
  legend rows of mathematics can be up to ~0.8 pt taller than `fp.legend()`'s.

## Developing

```bash
uv run pytest                       # the library, the examples' PDFs, the comparison
node --test "tests/*.test.mjs"      # the web runtime
uv run pytest -m smoke              # the web figure in a browser (Playwright)
```

Spec Kit features are under [`specs/`](specs/); releases are dated, see [AGENTS.md](AGENTS.md).

## Licence

MIT.
