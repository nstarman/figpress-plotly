"""The paper's units: points, converted to Plotly's CSS pixels."""

PX = 4 / 3  # CSS px per pt

# matplotlib's dash patterns in units of the line width (lines.scale_dashes, the default).
DASHES = {":": (1, 1.65), "--": (3.7, 1.6), "-.": (6.4, 1.6, 1, 1.6)}


def pt(v: float) -> float:
    """Points to Plotly's px."""
    return v * PX


def dash(style: str | tuple[float, ...], lw: float = 1.0) -> str:
    """A Plotly dash: a matplotlib style (`:`, `--`, `-.`) scaled by the line width `lw` (pt), as
    matplotlib scales it, or explicit on/off lengths in pt."""
    if isinstance(style, str):
        if style not in DASHES:
            raise ValueError(f"unknown dash style {style!r}; use one of {', '.join(DASHES)} or lengths in pt")
        lengths = [v * lw for v in DASHES[style]]
    else:
        lengths = list(style)
    return ",".join(f"{pt(v):.2f}px" for v in lengths)
