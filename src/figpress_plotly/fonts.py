"""The paper's fonts: the only fonts a figure uses, in print and on the web."""

import base64
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont

# The family name each role is known by in figures, in tex() and in the pages.
FAMILY = {"text": "fp-text", "bold": "fp-bold", "math_italic": "fp-math-it", "math_upright": "fp-math-rm"}


@dataclass(frozen=True)
class Fonts:
    """Font files by role: the figure's text, its bold, and mathematics' italic and upright."""

    text: Path
    bold: Path
    math_italic: Path
    math_upright: Path

    def __post_init__(self):
        for role in FAMILY:
            path = Path(getattr(self, role))
            if not path.is_file():
                raise FileNotFoundError(f"font for {role!r} not found: {path}")
            object.__setattr__(self, role, path)

    def files(self) -> dict[str, Path]:
        """Family name → font file."""
        return {FAMILY[role]: getattr(self, role) for role in FAMILY}

    def css(self) -> str:
        """@font-face rules with the fonts inlined."""
        return "".join(f"@font-face{{font-family:{fam};src:url(data:font/ttf;base64,{b64(path)})}}"
                       for fam, path in self.files().items())

    def width(self, text: str, role: str, size_pt: float) -> float:
        """The advance width of `text` set in `role` at `size_pt`, in pt (no kerning)."""
        cmap, hmtx, upem = _metrics(getattr(self, role))
        return sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text) * size_pt / upem


def b64(path: Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


@cache
def _metrics(path: Path):
    font = TTFont(path, lazy=True)
    return font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm


def dejavu(text: str = "serif") -> Fonts:
    """matplotlib's DejaVu fonts, as most matplotlib papers' figures use them: text and bold in
    DejaVu Serif (or Sans), mathematics in DejaVu Sans (mathtext's default `dejavusans`).
    Needs matplotlib, which ships them."""
    try:
        import matplotlib
    except ImportError as e:
        raise ImportError("dejavu() takes the fonts from matplotlib; install it or pass Fonts(...)") from e
    if text not in ("serif", "sans"):
        raise ValueError(f"text must be 'serif' or 'sans', not {text!r}")
    ttf = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
    face = "DejaVuSerif" if text == "serif" else "DejaVuSans"
    return Fonts(text=ttf / f"{face}.ttf", bold=ttf / f"{face}-Bold.ttf",
                 math_italic=ttf / "DejaVuSans-Oblique.ttf", math_upright=ttf / "DejaVuSans.ttf")
