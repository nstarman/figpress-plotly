from pathlib import Path

import pytest
from PIL import ImageFont

from figpress_plotly.fonts import FAMILY, Fonts, dejavu


def test_dejavu_serif_text_and_sans_math():
    f = dejavu()
    assert f.text.name == "DejaVuSerif.ttf" and f.bold.name == "DejaVuSerif-Bold.ttf"
    assert f.math_italic.name == "DejaVuSans-Oblique.ttf" and f.math_upright.name == "DejaVuSans.ttf"
    assert dejavu("sans").text.name == "DejaVuSans.ttf"


def test_a_missing_font_is_named(tmp_path):
    f = dejavu()
    with pytest.raises(FileNotFoundError, match="'bold'.*nope.ttf"):
        Fonts(text=f.text, bold=tmp_path / "nope.ttf", math_italic=f.math_italic, math_upright=f.math_upright)


def test_width_matches_the_font():
    f = dejavu()
    text = "Number of Streams"
    want = ImageFont.truetype(str(f.text), size=1000).getlength(text) / 1000 * 8
    assert f.width(text, "text", 8) == pytest.approx(want, rel=2e-3)


def test_css_inlines_every_family():
    css = dejavu().css()
    assert all(f"font-family:{fam};" in css for fam in FAMILY.values()) and css.count("base64,") == 4
