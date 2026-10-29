import pytest

from figpress_plotly.units import dash, pt


def test_pt_is_four_thirds_px():
    assert pt(3) == pytest.approx(4)


def test_matplotlib_dashes_scale_with_line_width():
    assert dash(":", 0.75) == "1.00px,1.65px"           # (1, 1.65) × 0.75 pt × 4/3 px/pt
    assert dash("--", 1.5) == f"{3.7 * 2:.2f}px,{1.6 * 2:.2f}px"
    assert dash("-.", 0.75).count(",") == 3


def test_explicit_lengths_are_points():
    assert dash((3, 1.5)) == "4.00px,2.00px"


def test_unknown_style_is_named():
    with pytest.raises(ValueError, match="'~'"):
        dash("~")
