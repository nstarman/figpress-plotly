"""The example's numbers, shared by the matplotlib reference and the figpress-plotly figure.

A synthetic figure in the style of a paper's: how many samples a two-sample test needs to tell a
base rate p_A from p_B = r p_A at several significance levels, with a band over r.
"""

import numpy as np
from matplotlib import colormaps, colors

PAGE = (244.8, 205.2)  # pt
FRAME = (34.0, 4.0, 203.0, 172.0)  # the axes: left, top, width, height (pt from the page's top left)
SPINE = 0.7  # pt

R_LO, R_PAPER, R_HI = 0.10, 0.50, 0.70
SIGMAS = [1, 2, 3, 5]
P_MIN, P_MAX = 0.001, 0.05
P = np.logspace(np.log10(P_MIN), np.log10(P_MAX), 400)
N_MIN, N_MAX = 1e2, 5e5
SURVEYS = [("Survey A forecast", 2300, 0.25, True), ("Current samples", 100, 0.45, False)]
P_SIM = 0.006

FONT = dict(tick=8.0, label=10.0, legend=7.0, survey=5.5, sim=7.0)
LEGEND = dict(at=(171.0, 7.0), ncol=2, handlelength=1.3, columnspacing=0.6, title="Two-sample test")


def n_required(z, p_a, p_b):
    num = (np.sqrt(p_a * (1 - p_a)) + np.sqrt(p_b * (1 - p_b))) ** 2
    return z**2 * num / (p_a - p_b) ** 2


def sigma_color(z):
    """The level's colour and alpha (1σ in grey)."""
    if z == 1:
        return (0.45, 0.45, 0.45), 0.30
    return colormaps["gnuplot_r"](0.12 + 0.70 * colors.Normalize(2, 5)(z))[:3], 1.0
