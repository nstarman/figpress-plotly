import plotly.graph_objects as go
import pytest

from figpress_plotly import Entry, dejavu, legend
from figpress_plotly.figure import Figure


def build(**kw):
    out = {}

    def fn(target):
        f = go.Figure()
        out["box"] = legend(f, [Entry(f"s{z}", f"${z}\\sigma$", band="red", edge=dict(color="red", width=0.6, dash=":"),
                                      line=dict(color="red", width=1.1)) for z in (1, 2, 3, 5)],
                            at=(171, 7), size=7, title="Two-sample test", ncol=2, handlelength=1.3, columnspacing=0.6, **kw)
        return f
    fig = Figure(fn, page=(244.8, 205.2), frame=(34, 4, 203, 172), fonts=dejavu()).build("web")
    return fig, out["box"]


def test_box_as_matplotlib_lays_it_out():
    # matplotlib's own legend with these parameters (measured): (171, 7) to (234.35, 40.6); widths here are
    # unkerned, so the title (the widest row) comes out ~0.35 pt wider
    _, box = build()
    assert box == pytest.approx((171, 7, 234.35, 40.6), abs=0.4)


def test_entries_fill_columns_and_carry_their_group():
    fig, _ = build()
    labels = [a for a in fig.layout.annotations if a.name and a.name.startswith("legend:")]
    assert [a.name for a in labels] == ["legend:s1", "legend:s2", "legend:s3", "legend:s5"]
    assert labels[0].x == labels[1].x < labels[2].x and labels[0].y > labels[1].y  # 1σ above 2σ
    assert all(a.captureevents for a in labels)  # clickable on the web
    handles = [s for s in fig.layout.shapes if s.name == "legend:s1"]
    assert {s.type for s in handles} == {"rect", "line"} and len(handles) == 3
