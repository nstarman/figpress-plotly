"""Text in the paper's fonts: the mathematics figures use, and labels placed as matplotlib places them."""

import html
import re
from functools import cache

from fontTools.ttLib import TTFont

from .figure import context
from .fonts import FAMILY
from .units import pt

# Chrome draws a Plotly annotation's line 0.123 em lower than the centre of the font's ascent and
# descent would put it (measured against matplotlib at 5.5–10 pt, DejaVu): text() corrects for it.
PLOTLY_DROP = 0.123
SCRIPT = 0.7  # a sub- or superscript's size, relative to its base (Plotly's <sub>/<sup>, matplotlib's)

GREEK = dict(zip(
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega".split(),
    "αβγδεζηθικλμνξπρστυφχψω"))
GREEK |= {k.capitalize(): v for k, v in zip(
    "gamma delta theta lambda xi pi sigma upsilon phi psi omega".split(), "ΓΔΘΛΞΠΣΥΦΨΩ")}
SYMBOLS = {"in": "∈", "times": "×", "cdot": "·", "pm": "±", "mp": "∓", "leq": "≤", "geq": "≥", "le": "≤", "ge": "≥",
           "sim": "∼", "approx": "≈", "neq": "≠", "infty": "∞", "propto": "∝", "prime": "′", "odot": "⊙",
           "rightarrow": "→", "to": "→", "ell": "ℓ", "partial": "∂", "nabla": "∇", ",": " ", ";": " ",
           " ": " ", "%": "%", "{": "{", "}": "}", "$": "$"}
UPRIGHT = {"rm", "mathrm", "text", "mathdefault"}
BINARY = set("+−=<>×·±∓≤≥∼≈≠∝∈→")  # spaced as mathtext spaces binary operators and relations
MEDIUM = "\u2005"  # a quarter em
_TOKEN = re.compile(r"\\([A-Za-z]+|.)|(.)", re.S)


def runs(s: str) -> list[tuple[str, str, str | None]]:
    """`s` as runs of (text, font role, script): outside `$…$` the figure's text (`"text"`); inside,
    mathematics as matplotlib's mathtext sets it — latin letters and lowercase Greek italic, the rest
    upright; `_` and `^` subscripts and superscripts; `\\rm{}`/`\\mathrm{}` upright."""
    out: list[tuple[str, str, str | None]] = []
    for i, part in enumerate(s.split("$")):
        if i % 2 == 0:
            if part:
                out.append((part, "text", None))
        else:
            toks = [m.group(1) and "\\" + m.group(1) or m.group(2) for m in _TOKEN.finditer(part)]
            toks = [t for t in toks if not t.isspace()]  # math mode ignores spaces
            start = len(out)
            _math(toks, 0, len(toks), upright=False, script=None, out=out)
            out[start:] = [(f"{MEDIUM}{t}{MEDIUM}" if t in BINARY and k > 0 and sc is None else t, r, sc)
                           for k, (t, r, sc) in enumerate(out[start:])]
    merged: list[tuple[str, str, str | None]] = []
    for r in out:
        if merged and merged[-1][1:] == r[1:]:
            merged[-1] = (merged[-1][0] + r[0], *r[1:])
        else:
            merged.append(r)
    return merged


def _group_end(toks, i):
    depth = 0
    for j in range(i, len(toks)):
        depth += toks[j] == "{"
        depth -= toks[j] == "}"
        if depth == 0:
            return j
    raise ValueError("unbalanced braces in math")


def _atom(toks, i, upright, script, out):
    """Write the atom at `i` (a group, a command with its argument, or a character); return the index after it."""
    t = toks[i]
    if t == "{":
        j = _group_end(toks, i)
        _math(toks, i + 1, j, upright, script, out)
        return j + 1
    if t.startswith("\\"):
        name = t[1:]
        if name in UPRIGHT:
            if i + 1 < len(toks) and toks[i + 1] == "{":
                return _atom(toks, i + 1, True, script, out)
            return i + 1  # {\rm …}: the caller's group continues upright (handled in _math)
        if name in GREEK:
            ch = GREEK[name]
            out.append((ch, "math_upright" if upright or ch.isupper() else "math_italic", script))
            return i + 1
        if name in SYMBOLS:
            out.append((SYMBOLS[name], "math_upright", script))
            return i + 1
        raise ValueError(f"unsupported math command \\{name}")
    ch = "−" if t == "-" else t
    out.append((ch, "math_italic" if ch.isalpha() and not upright else "math_upright", script))
    return i + 1


def _math(toks, i, end, upright, script, out):
    while i < end:
        t = toks[i]
        if t in ("\\rm", "\\mathrm") and (i + 1 >= end or toks[i + 1] != "{"):
            upright = True  # {\rm …}
            i += 1
            continue
        if t in ("_", "^"):  # no base in the math: it is the text before (`km s$^{-1}$`)
            if script is not None:
                raise ValueError("nested scripts are not supported")
            i = _atom(toks, i + 1, upright, "sub" if t == "_" else "sup", out)
            continue
        i = _atom(toks, i, upright, script, out)
        while i < end and toks[i] in ("_", "^"):
            if script is not None:
                raise ValueError("nested scripts are not supported")
            i = _atom(toks, i + 1, upright, "sub" if toks[i] == "_" else "sup", out)


def tex(s: str) -> str:
    """`s`, with `$…$` mathematics, as Plotly text in the paper's fonts."""
    parts = []
    for text, role, script in runs(s):
        t = html.escape(text, quote=False)
        if role != "text":
            t = f'<span style="font-family:{FAMILY[role]}">{t}</span>'
        parts.append(f"<{script}>{t}</{script}>" if script else t)
    return "".join(parts)


def width(s: str, size_pt: float, role: str = "text") -> float:
    """The width of `s` (with `$…$` mathematics) in pt; text outside mathematics is set in `role`."""
    fonts = context().fonts
    return sum(fonts.width(t, role if r == "text" else r, size_pt * (SCRIPT if sc else 1)) for t, r, sc in runs(s))


@cache
def _vmetrics(path) -> tuple[float, float]:
    f = TTFont(path, lazy=True)
    upem = f["head"].unitsPerEm
    return f["hhea"].ascent / upem, -f["hhea"].descent / upem


def text(fig, s: str, x: float, y: float, size: float, *, role: str = "text", color: str = "black",
         ha: str = "left", va: str = "baseline", data: bool = False, dx: float = 0.0, dy: float = 0.0, **kw) -> None:
    """Add the label `s` at page point (x, y) (pt from the top left), or at data point (x, y) when
    `data` (on a log axis, log10 of the value, as Plotly takes it), moved by (dx, dy) pt (dy down).
    Aligned as matplotlib aligns text: `ha` left, center or right; `va` baseline, or the top, bottom
    or centre of the line (the font's ascent and descent)."""
    ctx = context()
    asc, desc = _vmetrics(getattr(ctx.fonts, role))
    # Plotly centres a line on its font's ascent and descent: how far above (x, y) that centre goes.
    up = {"baseline": 0.0, "top": -asc * size, "bottom": desc * size, "center": -(asc - desc) / 2 * size}[va]
    up += ((asc - desc) / 2 + PLOTLY_DROP) * size - dy
    if data:
        where = dict(x=x, y=y, xref="x", yref="y", xshift=pt(dx), yshift=pt(up))
    else:
        where = dict(x=ctx.x(x + dx), y=ctx.y(y - up), xref="paper", yref="paper")
    fig.add_annotation(**where, xanchor=ha, yanchor="middle", text=tex(s), showarrow=False, borderpad=0, borderwidth=0,
                       font=dict(family=FAMILY[role], size=pt(size), color=color), **kw)


def stack(fig, base: str, sup: str, sub: str, x: float, y: float, size: float, *, color: str = "black",
          sup_rise: float = 0.36, sub_drop: float = 0.24, dx: float = 0.0, dy: float = 0.0, **kw) -> None:
    """`base` with a superscript and a subscript stacked after it (`p^{sim}_{A}`), its baseline at
    (x, y) as for `text`: Plotly cannot stack scripts, so each is its own label. Rise and drop are
    fractions of `size`, as mathtext's."""
    text(fig, base, x, y, size, color=color, dx=dx, dy=dy, **kw)
    after = dx + width(base, size)
    text(fig, sup, x, y, size * SCRIPT, color=color, dx=after, dy=dy - sup_rise * size, **kw)
    text(fig, sub, x, y, size * SCRIPT, color=color, dx=after, dy=dy + sub_drop * size, **kw)


def frac(fig, num: str, den: str, x: float, y: float, size: float, *, color: str = "black",
         gap: float = 0.25, rule: float = 0.065) -> None:
    """A fraction centred at page point x with its bar at y (pt): the numerator's baseline `gap`
    sizes above the bar and the denominator's top below it."""
    w = max(width(num, size), width(den, size)) + 0.2 * size
    ctx = context()
    fig.add_shape(type="line", xref="paper", yref="paper", x0=ctx.x(x - w / 2), x1=ctx.x(x + w / 2),
                  y0=ctx.y(y), y1=ctx.y(y), line=dict(color=color, width=pt(rule * size)), layer="above")
    text(fig, num, x, y - gap * size, size, color=color, ha="center")
    text(fig, den, x, y + gap * size, size, color=color, ha="center", va="top")
