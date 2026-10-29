"""A paper's style: its fonts and print settings, set once and shared by all its figures."""

from dataclasses import dataclass
from functools import cached_property

import plotly.graph_objects as go

from .fonts import FAMILY, Fonts
from .units import pt


@dataclass(frozen=True)
class Style:
    """Fonts and print settings in pt. A figure that names the style gets them as a Plotly template:
    defaults, so anything the figure sets itself wins."""

    fonts: Fonts
    size: float = 8.0  # text and tick labels
    label: float = 9.0  # axis titles
    spine: float = 0.7  # the frame's line width
    ticks: str = "inside"
    ticklen: float = 3.5
    tickwidth: float = 0.6
    minor_ticklen: float = 2.0
    line: float = 1.0  # traces' line width
    marker: float = 3.0  # traces' marker size
    margins: tuple[float, float, float, float] = (36.0, 6.0, 8.0, 30.0)  # left, top, right, bottom
    color: str = "black"

    @cached_property
    def template(self) -> go.layout.Template:
        text = dict(family=FAMILY["text"], size=pt(self.size), color=self.color)
        axis = dict(showline=True, linecolor=self.color, linewidth=pt(self.spine), mirror="ticks", ticks=self.ticks,
                    ticklen=pt(self.ticklen), tickwidth=pt(self.tickwidth), tickcolor=self.color, zeroline=False,
                    showgrid=False, tickfont=text, title=dict(font=dict(text, size=pt(self.label))),
                    minor=dict(ticklen=pt(self.minor_ticklen), tickwidth=pt(self.tickwidth * 0.8), tickcolor=self.color))
        return go.layout.Template(
            layout=dict(font=text, xaxis=axis, yaxis=axis, plot_bgcolor="white", paper_bgcolor="white",
                        legend=dict(font=text, bgcolor="rgba(255,255,255,0.8)", tracegroupgap=0), hoverlabel=dict(font_family=FAMILY["text"])),
            data=dict(scatter=[go.Scatter(line_width=pt(self.line), marker_size=pt(self.marker))]),
        )
