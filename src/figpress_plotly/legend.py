"""A legend drawn as matplotlib draws one, whose entries toggle their groups on the web."""

from dataclasses import dataclass

import numpy as np

from .figure import context
from .text import text, width
from .units import dash as to_dash
from .units import pt

ASCENT = 0.76  # where matplotlib puts a legend row's baseline, in sizes below the row's top


@dataclass(frozen=True)
class Entry:
    """A legend entry for `group`: its label and its handle, drawn from what is given — a band (fill
    colour), the band's upper edge and a line (each `dict(color=, width=pt, dash=)`)."""

    group: str
    label: str
    line: dict | None = None
    band: str | None = None
    edge: dict | None = None


def legend(fig, entries, at, size, *, title=None, ncol=1, handlelength=2.0, handleheight=0.7, handletextpad=0.8,
           columnspacing=2.0, labelspacing=0.5, borderpad=0.4, fill="rgba(255,255,255,0.8)", edgecolor="rgb(204,204,204)",
           linewidth=1.0, color="black") -> tuple[float, float, float, float]:
    """Draw a legend with its top-left corner at page point `at` (pt), laid out as matplotlib lays out
    `ax.legend(..., loc="upper left", bbox_to_anchor=at, borderaxespad=0)` with the same parameters
    (in units of `size`, matplotlib's names and defaults). Entries fill the columns top to bottom.
    Returns the box (left, top, right, bottom) in pt."""
    ctx = context()
    fs = size
    columns = [list(c) for c in np.array_split(np.array(entries, dtype=object), ncol) if len(c)]
    item_w = [[(handlelength + handletextpad) * fs + width(e.label, fs) for e in col] for col in columns]
    col_w = [max(ws) for ws in item_w]
    cols_w = sum(col_w) + columnspacing * fs * (len(columns) - 1)
    title_w = width(title, fs) if title else 0.0
    content = max(cols_w, title_w)
    rows = max(len(c) for c in columns)
    left, top = at
    pad, sep = borderpad * fs, labelspacing * fs
    # ponytail: every row one `size` tall, as for plain labels; matplotlib's mathtext labels can make a
    # row up to ~0.8 pt taller (seen at 7 pt). Measure label extents with mathtext if that ever exceeds 1 pt.
    height = 2 * pad + (fs + sep if title else 0) + rows * fs + (rows - 1) * sep
    right, bottom = left + content + 2 * pad, top + height

    r = 0.2 * fs  # matplotlib's fancybox corner
    x, y = ctx.x, ctx.y
    path = (f"M {x(left + r)},{y(top)} L {x(right - r)},{y(top)} Q {x(right)},{y(top)} {x(right)},{y(top + r)} "
            f"L {x(right)},{y(bottom - r)} Q {x(right)},{y(bottom)} {x(right - r)},{y(bottom)} "
            f"L {x(left + r)},{y(bottom)} Q {x(left)},{y(bottom)} {x(left)},{y(bottom - r)} "
            f"L {x(left)},{y(top + r)} Q {x(left)},{y(top)} {x(left + r)},{y(top)} Z")
    fig.add_shape(type="path", path=path, xref="paper", yref="paper", layer="above", fillcolor=fill,
                  line=dict(color=edgecolor, width=pt(linewidth)))

    row_top = top + pad
    if title:
        text(fig, title, left + pad + (content - title_w) / 2, row_top + ASCENT * fs, fs, color=color)
        row_top += fs + sep
    cx = left + pad + (content - cols_w) / 2
    for col, cw in zip(columns, col_w):
        for k, e in enumerate(col):
            base = row_top + k * (fs + sep) + ASCENT * fs  # the label's baseline; the handle stands on it
            h = handleheight * fs
            x0, x1 = cx, cx + handlelength * fs
            tag = f"legend:{e.group}"  # how the web runtime finds an entry's handle and label
            if e.band:
                fig.add_shape(type="rect", xref="paper", yref="paper", layer="above", x0=x(x0), x1=x(x1),
                              y0=y(base - 0.1 * h), y1=y(base - 0.9 * h), fillcolor=e.band, line_width=0, name=tag)
            for style, at_h in ((e.edge, 0.9), (e.line, 0.5)):
                if style:
                    fig.add_shape(type="line", xref="paper", yref="paper", layer="above", x0=x(x0), x1=x(x1),
                                  y0=y(base - at_h * h), y1=y(base - at_h * h), name=tag,
                                  line=dict(color=style["color"], width=pt(style["width"]),
                                            dash=to_dash(style["dash"], style["width"]) if style.get("dash") else None))
            text(fig, e.label, x1 + handletextpad * fs, base, fs, color=color, name=tag, captureevents=ctx.target == "web")
        cx += cw + columnspacing * fs
    return left, top, right, bottom
