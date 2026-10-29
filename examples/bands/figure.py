"""The example with figpress-plotly: one definition for the print figure and the web figure. It must
match reference.py's matplotlib figure within 1 pt.

    uv run figpress-plotly build examples/bands/figure.py:bands --out build/
"""

import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

import figpress_plotly as fp

sys.path.insert(0, str(Path(__file__).parent))
from common import (FONT, FRAME, LEGEND, N_MAX, N_MIN, P, P_MAX, P_MIN, P_SIM, PAGE, R_HI, R_LO,  # noqa: E402
                    R_PAPER, SIGMAS, SPINE, SURVEYS, n_required, sigma_color)


def rgba(rgb, a=1.0):
    r, g, b = (round(255 * c) for c in rgb)
    return f"rgba({r},{g},{b},{a:g})"


def gray(level, a=1.0):
    return rgba((float(level),) * 3, a)


@fp.figure(page=PAGE, frame=FRAME, fonts=fp.dejavu(), spine=SPINE,
           controls=[fp.Control("r", 0.12, 0.68, 0.02, value=R_PAPER, label="$r = p_{\\rm B}/p_{\\rm A}$")])
def bands(target, r=R_PAPER):
    fig = go.Figure()
    # matplotlib's stacking: each band and its edge at zorder max(SIGMAS) − z, the lines at 2.
    layers = []
    for n, z in enumerate(SIGMAS):
        color, alpha = sigma_color(z)
        lo, mid, hi = (n_required(z, P, k * P) for k in (R_LO, r, R_HI))
        g = f"s{z}"
        band = [go.Scatter(x=P, y=lo, line_width=0, hoverinfo="skip", showlegend=False, legendgroup=g),
                go.Scatter(x=P, y=hi, fill="tonexty", fillcolor=rgba(color, 0.15 * alpha), hoverinfo="skip",
                           showlegend=False, legendgroup=g,
                           line=dict(color=rgba(color, alpha), width=fp.pt(0.8), dash=fp.dash(":", 0.8)))]
        line = [go.Scatter(x=P, y=mid, legendgroup=g, showlegend=False, name=f"{z}σ",
                           line=dict(color=rgba(color, alpha), width=fp.pt(1.6)), customdata=np.c_[lo, hi],
                           hovertemplate=f"<b>{z}σ</b><br>p<sub>A</sub> = %{{x:.2%}}<br>N = %{{y:,.0f}} at r = {r:.2f}<br>"
                                         f"r ∈ [{R_LO:g}, {R_HI:g}]: %{{customdata[0]:,.0f}} – %{{customdata[1]:,.0f}}<extra></extra>")]
        layers += [(max(SIGMAS) - z, 2 * n, band), (2, 2 * n + 1, line)]
    for _, _, traces in sorted(layers, key=lambda t: t[:2]):
        fig.add_traces(traces)

    for name, n, level, lower in SURVEYS:
        fig.add_shape(type="line", xref="paper", x0=0, x1=1, yref="y", y0=n, y1=n, layer="above",
                      line=dict(color=gray(level), width=fp.pt(0.65), dash=fp.dash("--", 0.65)))
        x = P_MIN * 1.03 if lower else P_MAX * 0.97
        fp.text(fig, name, np.log10(x), np.log10(n * 1.12), FONT["survey"], role="bold", color=gray(level * 0.75),
                ha="left" if lower else "right", va="bottom", data=True)
    for x in (0.02, 0.03, 0.04):  # matplotlib's annotate arrows: 2 pt off each end (shrinkA/B)
        fig.add_annotation(x=np.log10(x), y=np.log10(2300 * 1.65), ax=np.log10(x), ay=np.log10(2300), axref="x", ayref="y",
                           text="", showarrow=True, arrowhead=2, arrowsize=2.2, arrowwidth=fp.pt(0.45),
                           arrowcolor=gray(0.25), standoff=fp.pt(2), startstandoff=fp.pt(2))

    fig.add_shape(type="line", x0=P_SIM, x1=P_SIM, yref="paper", y0=0, y1=1, layer="above",
                  line=dict(color=gray(0.3), width=fp.pt(0.9), dash=fp.dash("-.", 0.9)))
    fp.stack(fig, "$p$", r"$\rm sim$", r"$\rm A$", np.log10(P_SIM * 1.04), np.log10(N_MAX * 0.45), FONT["sim"],
             color=gray(0.3), data=True)

    fp.legend(fig, [fp.Entry(f"s{z}", f"${z}\\sigma$", band=rgba(c, 0.15 * a),
                             edge=dict(color=rgba(c, a), width=0.6, dash=":"), line=dict(color=rgba(c, a), width=1.1))
                    for z in SIGMAS for c, a in [sigma_color(z)]],
              at=LEGEND["at"], size=FONT["legend"], title=LEGEND["title"], ncol=LEGEND["ncol"],
              handlelength=LEGEND["handlelength"], columnspacing=LEGEND["columnspacing"],
              fill="rgba(255,255,255,0.9)", edgecolor=gray(0.7))

    major = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
    minor_x = [m * 10.0**k for k in (-3, -2) for m in range(2, 10) if not np.any(np.isclose(m * 10.0**k, major))]
    minor_x = [v for v in minor_x if v <= P_MAX]
    minor_y = [m * 10.0**k for k in range(2, 6) for m in range(2, 10) if m * 10.0**k <= N_MAX]
    axis = dict(type="log", showline=True, linecolor="black", linewidth=fp.pt(SPINE), mirror="ticks", ticks="inside",
                ticklen=fp.pt(3.5), tickwidth=fp.pt(0.8), tickcolor="black", zeroline=False,
                showgrid=True, gridcolor=gray(0.5, 0.4), gridwidth=fp.pt(0.35), griddash=fp.dash(":", 0.35),
                tickfont=dict(family="fp-text", size=fp.pt(FONT["tick"]), color="black"),
                title=dict(font=dict(family="fp-text", size=fp.pt(FONT["label"]), color="black")))
    minor = dict(ticks="inside", ticklen=fp.pt(2), tickwidth=fp.pt(0.6), tickcolor="black", showgrid=False)
    fig.update_xaxes(axis, range=[np.log10(P_MIN), np.log10(P_MAX)], tickvals=major,
                     ticktext=["0.1%", "0.2%", "0.5%", "1%", "2%", "5%"], minor=dict(minor, tickvals=minor_x),
                     title_text=fp.tex(r"Base rate $p_{\rm A}$"), title_standoff=fp.pt(4), ticklabelstandoff=round(fp.pt(-1.45)))
    fig.update_yaxes(axis, range=[np.log10(N_MIN), np.log10(N_MAX)], tickvals=[1e2, 1e3, 1e4, 1e5],
                     ticktext=[f"10<sup>{k}</sup>" for k in range(2, 6)], minor=dict(minor, tickvals=minor_y),
                     title_text="Required sample size", title_standoff=fp.pt(4), ticklabelstandoff=round(fp.pt(2.7)))
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                      hovermode="closest" if target == "web" else False)
    return fig
