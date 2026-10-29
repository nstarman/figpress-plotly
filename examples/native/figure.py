"""A new figure, native from the start: no matplotlib figure to match. The PDF goes into the paper,
the web page onto its site.

    uv run figpress-plotly build examples/native/figure.py:rotation --out build/
"""

import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

import figpress_plotly as fp

sys.path.insert(0, str(Path(__file__).parent))
from style import COLUMN, STYLE  # noqa: E402

R = np.linspace(0.5, 30, 300)  # kpc
R_DATA = np.arange(2, 30, 2.5)
RNG = np.random.default_rng(1)


def disk(r):
    return 180 * np.sqrt(r / 4) * np.exp(-r / 8)


def halo(r, v0=170, rc=5):
    return v0 * np.sqrt(1 - rc / r * np.arctan(r / rc))


def total(r):
    return np.hypot(disk(r), halo(r))


V_DATA = total(R_DATA) + RNG.normal(0, 6, R_DATA.size)
V_ERR = np.full(R_DATA.size, 8.0)


@fp.figure(page=(COLUMN, 170), style=STYLE)
def rotation(target):
    kms = fp.tex(r"km s$^{-1}$")
    fig = go.Figure()
    hi, lo = total(R) * 1.05, total(R) * 0.95
    fig.add_traces([
        go.Scatter(x=R, y=lo, line_width=0, hoverinfo="skip", showlegend=False, legendgroup="model"),
        go.Scatter(x=R, y=hi, fill="tonexty", fillcolor="rgba(31,119,180,0.15)", line_width=0, hoverinfo="skip",
                   showlegend=False, legendgroup="model"),
        go.Scatter(x=R, y=total(R), name="Model", legendgroup="model", line_color="rgb(31,119,180)",
                   hovertemplate=f"r = %{{x:.1f}} kpc<br>v = %{{y:.0f}} {kms}<extra>model</extra>"),
        go.Scatter(x=R, y=disk(R), name="Disk", line=dict(color="rgb(90,90,90)", dash=fp.dash("--", 1.0)),
                   hovertemplate=f"%{{y:.0f}} {kms}<extra>disk</extra>"),
        go.Scatter(x=R, y=halo(R), name="Halo", line=dict(color="rgb(90,90,90)", dash=fp.dash(":", 1.0)),
                   hovertemplate=f"%{{y:.0f}} {kms}<extra>halo</extra>"),
        go.Scatter(x=R_DATA, y=V_DATA, name="Data", mode="markers", marker_color="black",
                   error_y=dict(array=V_ERR, thickness=fp.pt(0.6), width=fp.pt(1.5), color="black"),
                   hovertemplate=f"r = %{{x:.1f}} kpc<br>v = %{{y:.0f}} ± 8 {kms}<extra>data</extra>"),
    ])
    fig.update_xaxes(range=[0, 30], title_text=fp.tex(r"$r$ (kpc)"))
    fig.update_yaxes(range=[0, 300], title_text=fp.tex(r"$v_{\rm c}$ (km s$^{-1}$)"))
    fig.update_layout(legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top"),
                      hovermode="closest" if target == "web" else False)
    return fig
