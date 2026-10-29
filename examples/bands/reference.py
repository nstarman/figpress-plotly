"""The example drawn with matplotlib, as a paper's figure is: the reference figure.py must match.

    uv run python examples/bands/reference.py      # writes examples/bands/reference.pdf
"""

from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.legend_handler import HandlerBase  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.ticker import NullFormatter  # noqa: E402

from common import (FONT, FRAME, LEGEND, N_MAX, N_MIN, P, P_MAX, P_MIN, P_SIM, PAGE, R_HI, R_LO,  # noqa: E402
                    R_PAPER, SIGMAS, SPINE, SURVEYS, n_required, sigma_color)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42, "axes.linewidth": SPINE, "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True, "xtick.labelsize": FONT["tick"], "ytick.labelsize": FONT["tick"],
    "axes.labelsize": FONT["label"],
})


class BandLine(HandlerBase):
    """A legend handle: the band, its dotted upper edge and the line."""

    def create_artists(self, legend, orig, xd, yd, width, height, fontsize, trans):
        color, alpha = orig.band
        top = yd + 0.9 * height
        return [Rectangle((xd, yd + 0.1 * height), width, 0.8 * height, color=color, alpha=0.15 * alpha, lw=0, transform=trans),
                Line2D([xd, xd + width], [top, top], color=color, alpha=alpha, lw=0.6, ls=":", transform=trans),
                Line2D([xd, xd + width], [yd + height / 2] * 2, color=color, alpha=alpha, lw=1.1, transform=trans)]


def main(out: Path) -> None:
    w, h = PAGE
    left, top, fw, fh = FRAME
    fig = plt.figure(figsize=(w / 72, h / 72))
    ax = fig.add_axes((left / w, 1 - (top + fh) / h, fw / w, fh / h))
    handles = []
    for z in SIGMAS:
        color, alpha = sigma_color(z)
        lo, mid, hi = (n_required(z, P, r * P) for r in (R_LO, R_PAPER, R_HI))
        ax.fill_between(P, lo, hi, color=color, alpha=0.15 * alpha, lw=0, zorder=max(SIGMAS) - z)
        ax.plot(P, hi, color=color, alpha=alpha, lw=0.8, ls=":", zorder=max(SIGMAS) - z)
        ax.plot(P, mid, color=color, alpha=alpha, lw=1.6)
        handle = Line2D([], [])
        handle.band = (color, alpha)
        handles.append(handle)
    for name, n, gray, lower in SURVEYS:
        ax.axhline(n, color=str(gray), lw=0.65, ls="--")
        x = P_MIN * 1.03 if lower else P_MAX * 0.97
        ax.text(x, n * 1.12, name, ha="left" if lower else "right", va="bottom", fontsize=FONT["survey"],
                fontweight="bold", color=str(gray * 0.75))
    ax.axvline(P_SIM, color="0.3", lw=0.9, ls="-.")
    ax.text(P_SIM * 1.04, N_MAX * 0.45, r"$p^{\rm sim}_{\rm A}$", fontsize=FONT["sim"], color="0.3", va="baseline")
    for x in (0.02, 0.03, 0.04):
        ax.annotate("", xy=(x, 2300 * 1.65), xytext=(x, 2300), arrowprops=dict(arrowstyle="-|>", lw=0.45, color="0.25"))
    ax.set(xscale="log", yscale="log", xlim=(P_MIN, P_MAX), ylim=(N_MIN, N_MAX))
    ax.set_xticks([0.001, 0.002, 0.005, 0.01, 0.02, 0.05], ["0.1%", "0.2%", "0.5%", "1%", "2%", "5%"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.grid(True, which="major", ls=":", lw=0.35, color="0.5", alpha=0.4)
    ax.set_xlabel(r"Base rate $p_{\rm A}$")
    ax.set_ylabel("Required sample size")
    lx, ly = LEGEND["at"]
    ax.legend(handles, [f"${z}\\sigma$" for z in SIGMAS], handler_map={Line2D: BandLine()}, ncol=LEGEND["ncol"],
              title=LEGEND["title"], fontsize=FONT["legend"], title_fontsize=FONT["legend"],
              handlelength=LEGEND["handlelength"], columnspacing=LEGEND["columnspacing"],
              loc="upper left", bbox_to_anchor=(lx / w, 1 - ly / h), bbox_transform=fig.transFigure,
              borderaxespad=0, framealpha=0.9, edgecolor="0.7", fancybox=True)
    fig.savefig(out)


if __name__ == "__main__":
    main(Path(__file__).with_name("reference.pdf"))
