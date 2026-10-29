"""A figure: the author's `build(target, **params)` with its page, frame, fonts and controls."""

import inspect
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path

import plotly.graph_objects as go

from .fonts import FAMILY, Fonts
from .units import pt

TARGETS = ("pdf", "web")
_current: ContextVar["Context"] = ContextVar("figpress_plotly_context")


@dataclass(frozen=True)
class Context:
    """The figure being built: its target and its page geometry, for placing marks in page points."""

    target: str
    page: tuple[float, float]
    plot: tuple[float, float, float, float]  # Plotly's plot area in pt: left, top, width, height
    fonts: Fonts

    def x(self, x_pt: float) -> float:
        """A horizontal position on the page (pt from the left) in Plotly's paper coordinates."""
        return (x_pt - self.plot[0]) / self.plot[2]

    def y(self, y_pt: float) -> float:
        """A vertical position on the page (pt from the top) in Plotly's paper coordinates."""
        return 1 - (y_pt - self.plot[1]) / self.plot[3]

    def width(self, text: str, role: str, size_pt: float) -> float:
        """The width of `text` in pt, set in the font of `role` (see Fonts)."""
        return self.fonts.width(text, role, size_pt)


def context() -> Context:
    """The figure being built; only inside a figure's `build`."""
    try:
        return _current.get()
    except LookupError:
        raise RuntimeError("fp.context() is only available while a figure is being built") from None


@dataclass(frozen=True)
class Control:
    """A parameter of the figure the reader can change on the web, over `lo, lo + step, …, hi`;
    `value` is the paper's."""

    name: str
    lo: float
    hi: float
    step: float
    value: float
    label: str = ""
    format: str = ".2f"

    def __post_init__(self):
        if not (self.lo < self.hi and self.step > 0):
            raise ValueError(f"control {self.name!r}: need lo < hi and step > 0")


class Figure:
    """A paper figure: `build(target, **params)` gives it for print (`"pdf"`) or the web (`"web"`)."""

    def __init__(self, fn, *, page, frame=None, margins=None, fonts=None, style=None, controls=(), name=None,
                 spine=None):
        w, h = page
        if frame is not None and margins is not None:
            raise ValueError("give the frame or the margins, not both")
        if frame is None:
            margins = margins if margins is not None else style.margins if style else None
            if margins is None:
                raise ValueError("give the frame, the margins or a style (whose margins are used)")
            ml, mt, mr, mb = margins
            frame = (ml, mt, w - ml - mr, h - mt - mb)
        fonts = fonts or (style.fonts if style else None)
        if fonts is None:
            raise ValueError("give the fonts, or a style that has them")
        spine = spine if spine is not None else style.spine if style else 0.7
        left, top, fw, fh = frame
        if min(w, h, fw, fh) <= 0 or left < 0 or top < 0 or left + fw > w or top + fh > h:
            raise ValueError(f"frame {frame} must lie inside the page {page} (pt)")
        params = inspect.signature(fn).parameters
        for c in controls:
            if c.name not in params:
                raise ValueError(f"control {c.name!r} is not a parameter of {fn.__name__}()")
        self.fn, self.page, self.frame, self.fonts, self.style = fn, (w, h), tuple(frame), fonts, style
        self.controls, self.name = tuple(controls), name or fn.__name__
        # The frame is where the paper's spines are (matplotlib centres them on the axes' edge);
        # Plotly draws axis lines just outside its plot area, so that is inset by half a line.
        i = spine / 2
        self.plot = (left + i, top + i, fw - 2 * i, fh - 2 * i)
        self.__doc__, self.__wrapped__ = fn.__doc__, fn

    def build(self, target: str = "pdf", **params) -> go.Figure:
        if target not in TARGETS:
            raise ValueError(f"target must be one of {TARGETS}, not {target!r}")
        token = _current.set(Context(target, self.page, self.plot, self.fonts))
        try:
            fig = self.fn(target, **params)
        finally:
            _current.reset(token)
        if self.style is not None:
            fig.update_layout(template=self.style.template)  # defaults: the figure's own settings win
        w, h = self.page
        left, top, pw, ph = self.plot
        fig.update_layout(
            width=pt(w), height=pt(h), autosize=False,
            margin=dict(l=pt(left), t=pt(top), r=pt(w - left - pw), b=pt(h - top - ph), pad=0),
        )
        fig.update_xaxes(automargin=False)
        fig.update_yaxes(automargin=False)
        if fig.layout.font.family is None:
            fig.update_layout(font_family=FAMILY["text"])
        return fig

    def write_pdf(self, path, **params) -> Path:
        from .pdf import write_pdf

        return write_pdf(self.build("pdf", **params), Path(path), self.page, self.fonts)

    def write_web(self, out, single_file=None, **params) -> Path:
        from .web import write_web

        return write_web(self, Path(out), single_file, **params)

    def __call__(self, target: str = "pdf", **params) -> go.Figure:
        return self.build(target, **params)


def figure(*, page, frame=None, margins=None, fonts: Fonts | None = None, style=None, controls=(), name=None,
           spine=None):
    """Decorate `build(target, **params)` with its page (pt) and either its exact frame (left, top,
    width, height) or its margins (left, top, right, bottom), its fonts, its paper `style` (which
    supplies fonts, margins and the frame's line width `spine` unless given) and its controls."""
    return lambda fn: Figure(fn, page=page, frame=frame, margins=margins, fonts=fonts, style=style,
                             controls=controls, name=name, spine=spine)
