"""Measure a figure's PDF against the paper's: an overlay image and how far each element moved."""

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
from PIL import Image

DPI = 600


@dataclass(frozen=True)
class Element:
    kind: str  # "text" or "frame"
    name: str
    dx: float  # pt, new − reference (x right, y down); nan when missing
    dy: float
    ok: bool


@dataclass
class Comparison:
    tol: float
    elements: list[Element] = field(default_factory=list)
    overlay: Path | None = None

    @property
    def ok(self) -> bool:
        return all(e.ok for e in self.elements)

    def report(self) -> str:
        lines = [f"{e.kind:5} {e.name:28} {e.dx:+6.2f} {e.dy:+6.2f}  {'ok' if e.ok else 'FAIL'}" for e in self.elements]
        bad = sum(not e.ok for e in self.elements)
        lines.append(f"{len(self.elements)} elements, {bad} beyond {self.tol:g} pt" if bad else
                     f"{len(self.elements)} elements, all within {self.tol:g} pt")
        return "\n".join(lines)


def compare(new, reference, tol: float = 1.0, overlay=None) -> Comparison:
    """Compare two one-page PDFs of the same size: text (matched by content) and the axes frame."""
    new_page, ref_page = _page(new), _page(reference)
    if not np.allclose(new_page.get_size(), ref_page.get_size(), atol=0.1):
        raise ValueError(f"page sizes differ: {new_page.get_size()} vs {ref_page.get_size()} pt")
    out = Comparison(tol)
    out.elements += _texts(_chars(new_page), _chars(ref_page), tol)
    new_img, ref_img = _render(new_page), _render(ref_page)
    out.elements += _frame(_lines(new_img), _lines(ref_img), tol)
    if overlay is not None:
        # The reference shows cyan where only it is dark, the new figure red; both: dark.
        rgb = np.stack([ref_img, new_img, new_img], axis=-1)
        Image.fromarray(rgb).save(overlay)
        out.overlay = Path(overlay)
    return out


def _page(path):
    return pdfium.PdfDocument(str(path))[0]


def _render(page) -> np.ndarray:
    return np.asarray(page.render(scale=DPI / 72).to_pil().convert("L"))


def _chars(page) -> list[tuple[str, float, float, float, tuple]]:
    """Every visible character: (char, angle, centre x, centre y, loose box), in pt from the top left."""
    tp = page.get_textpage()
    h = page.get_height()
    out = []
    for i in range(tp.count_chars()):
        c = tp.get_text_range(i, 1)
        if not c.strip():
            continue
        l, b, r, t = tp.get_charbox(i, loose=True)
        angle = pdfium.raw.FPDFText_GetCharAngle(tp, i)
        out.append((c, angle, (l + r) / 2, h - (b + t) / 2, (l, h - t, r, h - b)))
    return out


def _groups(chars) -> list[list]:
    """The reference's characters in words: consecutive, at the same angle, next to each other along
    the reading direction and overlapping across it (so a rotated label is one word, and lines
    stacked one above the other are not)."""
    groups = []
    for ch in chars:
        c, a, x, y, (l, t, r, b) = ch
        cos, sin = math.cos(a), math.sin(a)
        # In the reading frame: u along the text, v across it (pt). pdfium's angle is the reading
        # direction in these top-down page coordinates.
        corners = [(px * cos + py * sin, -px * sin + py * cos) for px in (l, r) for py in (t, b)]
        u0, u1 = min(q[0] for q in corners), max(q[0] for q in corners)
        v0, v1 = min(q[1] for q in corners), max(q[1] for q in corners)
        size = max(v1 - v0, 1.0)
        if groups:
            pa, pu0, pu1, pv0, pv1 = groups[-1][-1][5:]
            overlap = min(v1, pv1) - max(v0, pv0)
            if (abs(a - pa) < 0.1 and pu0 - 0.1 * size <= u0 <= pu1 + 0.6 * size
                    and overlap >= 0.3 * min(size, pv1 - pv0)):
                groups[-1].append((*ch, a, u0, u1, v0, v1))
                continue
        groups.append([(*ch, a, u0, u1, v0, v1)])
    return groups


def _texts(new_chars, ref_chars, tol) -> list[Element]:
    """Each reference word found in the new figure by one rigid shift of all its characters."""
    by_char = {}
    for c, _, x, y, _ in new_chars:
        by_char.setdefault(c, []).append((x, y))
    by_char = {c: np.array(v) for c, v in by_char.items()}
    out, seen = [], {}
    for g in _groups(ref_chars):
        text = "".join(ch[0] for ch in g)
        seen[text] = seen.get(text, 0) + 1
        name = text if seen[text] == 1 else f"{text} #{seen[text]}"
        pts = np.array([(ch[2], ch[3]) for ch in g])
        if any(ch[0] not in by_char for ch in g):
            out.append(Element("text", name, float("nan"), float("nan"), False))
            continue

        def cost(shift):
            return sum(np.min(np.hypot(*(by_char[ch[0]] - (p + shift)).T)) for ch, p in zip(g, pts))

        first = by_char[g[0][0]]
        near = first[np.hypot(*(first - pts[0]).T) < 20]
        if not len(near):
            out.append(Element("text", name, float("nan"), float("nan"), False))
            continue
        shift = min((c - pts[0] for c in near), key=lambda s: (round(cost(s), 3), math.hypot(*s)))  # ties: the nearer
        if cost(shift) / len(g) > max(tol, 1.0) * 2:  # not this word: its letters are not where the shift puts them
            out.append(Element("text", name, float("nan"), float("nan"), False))
            continue
        dx, dy = (float(v) for v in shift)
        out.append(Element("text", name, dx, dy, abs(dx) <= tol and abs(dy) <= tol))
    return out


def _lines(img: np.ndarray) -> dict[str, float]:
    """The frame: the outermost long straight dark lines (continuous over half the page), in pt."""
    dark = img < 100
    found = {}
    for axis, (lo, hi) in ((0, ("left", "right")), (1, ("top", "bottom"))):
        runs = _longest_runs(dark if axis == 0 else dark.T)  # per column (axis 0) or per row
        idx = np.flatnonzero(runs > 0.5 * (dark.shape[0] if axis == 0 else dark.shape[1]))
        if idx.size:
            groups = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
            found[lo] = groups[0].mean() * 72 / DPI
            found[hi] = groups[-1].mean() * 72 / DPI
    return found


def _longest_runs(m: np.ndarray) -> np.ndarray:
    """The longest run of True down each column."""
    best = np.zeros(m.shape[1], int)
    cur = np.zeros(m.shape[1], int)
    for row in m:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def _frame(new, ref, tol) -> list[Element]:
    out = []
    for edge, v in ref.items():
        if edge not in new:
            out.append(Element("frame", edge, float("nan"), float("nan"), False))
            continue
        d = new[edge] - v
        dx, dy = (d, 0.0) if edge in ("left", "right") else (0.0, d)
        out.append(Element("frame", edge, dx, dy, abs(d) <= tol))
    return out
