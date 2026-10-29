"""The paper's style, shared by all its figures: set once, here.

STIX is the Times-like face of journals set in Times (AASTeX and others). Any font files work;
these ship with matplotlib, which is only where this example finds them.
"""

from pathlib import Path

import matplotlib

import figpress_plotly as fp

TTF = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
FONTS = fp.Fonts(text=TTF / "STIXGeneral.ttf", bold=TTF / "STIXGeneralBol.ttf",
                 math_italic=TTF / "STIXGeneralItalic.ttf", math_upright=TTF / "STIXGeneral.ttf")

STYLE = fp.Style(fonts=FONTS, size=8, label=9, margins=(38, 6, 8, 28))
COLUMN = 242.0  # pt: one column of a two-column journal page
