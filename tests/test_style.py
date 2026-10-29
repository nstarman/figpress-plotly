import plotly.graph_objects as go
import pytest

import figpress_plotly as fp

STYLE = fp.Style(fonts=fp.dejavu(), size=7, spine=0.5, margins=(30, 5, 5, 25))


def test_a_style_supplies_fonts_margins_and_spine():
    f = fp.figure(page=(200, 100), style=STYLE)(lambda target: go.Figure())
    assert f.fonts == STYLE.fonts and f.frame == (30, 5, 165, 70)
    assert f.plot == pytest.approx((30.25, 5.25, 164.5, 69.5))  # inset by half the 0.5 pt spine


def test_the_style_is_a_template_the_figure_overrides():
    def fn(target):
        fig = go.Figure(go.Scatter(x=[1, 2], y=[1, 2]))
        fig.update_xaxes(ticklen=fp.pt(6))
        return fig
    fig = fp.figure(page=(200, 100), style=STYLE)(fn).build("pdf")
    t = fig.layout.template.layout
    assert t.font.size == pytest.approx(fp.pt(7)) and t.font.family == "fp-text"
    assert t.xaxis.ticklen == pytest.approx(fp.pt(3.5)) and t.xaxis.linewidth == pytest.approx(fp.pt(0.5))
    assert fig.layout.xaxis.ticklen == pytest.approx(fp.pt(6))  # the figure's own setting
    assert fig.layout.template.data.scatter[0].line.width == pytest.approx(fp.pt(1.0))
