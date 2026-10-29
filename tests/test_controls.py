import base64
import json

import numpy as np
import plotly.graph_objects as go
import pytest

from figpress_plotly import Control, dejavu
from figpress_plotly import controls as ctl
from figpress_plotly.figure import Figure

X = np.linspace(0, 1, 5)


def make(fn, **c):
    c = {"lo": 0.5, "hi": 1.5, "step": 0.5, "value": 1.0, **c}
    return Figure(fn, page=(100, 50), frame=(10, 5, 80, 40), fonts=dejavu(), controls=[Control("k", **c)])


def line(target, k=1.0):
    fig = go.Figure(go.Scatter(x=X, y=k * X, hovertemplate=f"k = {k}"))
    fig.add_shape(type="line", x0=0, x1=1, y0=0.5, y1=0.5)
    fig.add_annotation(x=0.5, y=k, text=f"k = {k}", showarrow=False)
    return fig


def packed(fig):
    base = json.loads(fig.build("web").to_json())
    return ctl.pack(fig, base)[0]


def floats(v):
    return np.frombuffer(base64.b64decode(v["bdata"]), dtype=v["dtype"])


def test_only_what_changes_is_stored():
    c = packed(make(line))
    assert c["settings"] == [0.5, 1.0, 1.5] and c["index"] == 1
    paths = [tuple(d["path"]) for d in c["diffs"]]
    assert ("data", 0, "y") in paths and ("data", 0, "hovertemplate") in paths
    assert ("layout", "annotations", 0, "y") in paths and ("layout", "annotations", 0, "text") in paths
    assert not any(p[:2] == ("layout", "shapes") for p in paths) and ("data", 0, "x") not in paths


def test_values_per_setting():
    c = packed(make(line))
    y = next(d for d in c["diffs"] if d["path"] == ["data", 0, "y"])
    np.testing.assert_allclose([floats(v) for v in y["values"]], [k * X for k in (0.5, 1.0, 1.5)], rtol=1e-6)
    assert y["values"][0]["dtype"] == "f4"  # stored at 6 significant digits
    text = next(d for d in c["diffs"] if d["path"] == ["layout", "annotations", 0, "text"])
    assert text["values"] == ["k = 0.5", "k = 1.0", "k = 1.5"]


def test_a_change_of_structure_is_named():
    def grows(target, k=1.0):
        fig = line(target, k)
        if k > 1:
            fig.add_annotation(x=0, y=0, text="extra")
        return fig
    with pytest.raises(ValueError, match="structure changes .* layout/annotations"):
        packed(make(grows))


def test_the_size_cap(monkeypatch):
    monkeypatch.setattr(ctl, "MAX_NUMBERS", 10)
    with pytest.raises(ValueError, match="numbers to store"):
        packed(make(line))


def test_the_paper_value_snaps_to_a_setting():
    with pytest.warns(UserWarning, match="not a setting; using 1.0"):
        c = packed(make(line, value=1.1))
    assert c["index"] == 1
