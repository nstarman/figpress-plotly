import plotly.graph_objects as go
import pytest

import figpress_plotly as fp
from figpress_plotly.figure import Control, Figure, context
from figpress_plotly.fonts import dejavu

FONTS = dejavu()


def make(page=(200, 100), frame=(30, 10, 160, 70), **kw):
    def bars(target, k=1.0):
        ctx = context()
        fig = go.Figure(go.Scatter(x=[0, 1], y=[0, k]))
        fig.add_annotation(x=ctx.x(30), y=ctx.y(10), text=target, xref="paper", yref="paper")
        return fig
    return Figure(bars, page=page, frame=frame, fonts=FONTS, **kw)


def test_page_and_plot_area_in_points():
    fig = make(spine=1.0).build("pdf")
    assert fig.layout.width == pytest.approx(200 * 4 / 3) and fig.layout.height == pytest.approx(100 * 4 / 3)
    m = fig.layout.margin
    assert (m.l, m.t, m.r, m.b) == pytest.approx((30.5 * 4 / 3, 10.5 * 4 / 3, 10.5 * 4 / 3, 20.5 * 4 / 3))
    assert fig.layout.font.family == "fp-text" and fig.layout.xaxis.automargin is False


def test_context_places_page_points():
    a = make(spine=0).build("web").layout.annotations[0]
    assert (a.x, a.y, a.text) == (0, 1, "web")


def test_context_only_inside_a_build():
    with pytest.raises(RuntimeError, match="being built"):
        context()


def test_frame_must_be_inside_the_page():
    with pytest.raises(ValueError, match="inside the page"):
        make(frame=(30, 10, 180, 70))


def test_controls_must_be_parameters():
    make(controls=[Control("k", 0, 2, 0.5, value=1)])
    with pytest.raises(ValueError, match="'q' is not a parameter"):
        make(controls=[Control("q", 0, 2, 0.5, value=1)])


def test_unknown_target():
    with pytest.raises(ValueError, match="target"):
        make().build("png")


def test_decorator():
    @fp.figure(page=(100, 50), frame=(10, 5, 80, 40), fonts=FONTS)
    def f(target):
        return go.Figure()
    assert f.name == "f" and f("pdf").layout.width == pytest.approx(100 * 4 / 3)


def test_margins_instead_of_a_frame():
    f = Figure(lambda target: go.Figure(), page=(200, 100), margins=(30, 10, 10, 20), fonts=FONTS, spine=0)
    assert f.frame == (30, 10, 160, 70)
    with pytest.raises(ValueError, match="not both"):
        Figure(lambda target: go.Figure(), page=(200, 100), frame=(30, 10, 160, 70), margins=(1, 1, 1, 1), fonts=FONTS)
    with pytest.raises(ValueError, match="margins or a style"):
        Figure(lambda target: go.Figure(), page=(200, 100), fonts=FONTS)
