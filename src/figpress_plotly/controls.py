"""Controls on the web: every setting built in Python, and what differs from the paper's figure kept.

The page holds the figure at the paper's values; for each control, each leaf that changes (a trace's
`y`, a shape's `y0`, a label's text, a hover template) with its value at every setting. The runtime
puts those values in: no science runs in the browser, and nothing the author's build does not change
can move.
"""

import base64
import json
import warnings

import numpy as np

from .text import tex

MAX_NUMBERS = 5_000_000  # stored per page, across controls
DIGITS = 6  # significant digits kept for stored numbers


def settings(c) -> list[float]:
    """The control's settings, lo to hi in steps."""
    n = int(round((c.hi - c.lo) / c.step))
    return [float(round(c.lo + k * c.step, 10)) for k in range(n + 1)]


def paper_index(c, values: list[float]) -> int:
    """The setting at the paper's value (snapped to the nearest, with a warning)."""
    i = int(np.argmin([abs(v - c.value) for v in values]))
    if not np.isclose(values[i], c.value, rtol=0, atol=c.step * 1e-6):
        warnings.warn(f"control {c.name!r}: the paper's value {c.value} is not a setting; using {values[i]}", stacklevel=3)
    return i


def _is_array(v) -> bool:
    return isinstance(v, dict) and "bdata" in v


def _leaves(a, b, path=()):
    """The paths where `b` differs from `a`; the two must have the same structure."""
    if _is_array(a) or _is_array(b) or not isinstance(a, (dict, list)):
        if a != b:
            yield path
        return
    if type(a) is not type(b) or (isinstance(a, list) and len(a) != len(b)) or (isinstance(a, dict) and a.keys() != b.keys()):
        raise ValueError(f"the figure's structure changes with the control at {'/'.join(map(str, path)) or 'the top'}: "
                         "a control may change values, not add or remove traces, shapes or labels")
    for k in (a.keys() if isinstance(a, dict) else range(len(a))):
        yield from _leaves(a[k], b[k], (*path, k))


def _get(tree, path):
    for k in path:
        tree = tree[k]
    return tree


def _compact(v):
    """A value as stored: arrays of floats at DIGITS significant digits, as float32."""
    if _is_array(v) and v.get("dtype") == "f8":
        x = np.frombuffer(base64.b64decode(v["bdata"]), dtype="<f8")
        x = np.array([float(f"{f:.{DIGITS - 1}e}") for f in x], dtype="<f4")
        return {**v, "dtype": "f4", "bdata": base64.b64encode(x.tobytes()).decode()}
    return v


def _count(v) -> int:
    if _is_array(v):
        return len(base64.b64decode(v["bdata"])) // np.dtype(v["dtype"]).itemsize
    return len(v) if isinstance(v, list) else 1


def pack(figure, base: dict, **params) -> list[dict]:
    """The controls of `figure` for its page: `base` is the web figure's JSON at the paper's values."""
    out, total = [], 0
    for c in figure.controls:
        values = settings(c)
        index = paper_index(c, values)
        built = [json.loads(figure.build("web", **{**params, c.name: v}).to_json()) for v in values]
        paths = sorted({p for b in built for p in _leaves(base, b)}, key=lambda p: tuple(map(str, p)))
        diffs = [{"path": list(p), "values": [_compact(_get(b, p)) for b in built]} for p in paths]
        total += sum(_count(v) for d in diffs for v in d["values"])
        if total > MAX_NUMBERS:
            raise ValueError(f"control {c.name!r}: {total:,} numbers to store (over {MAX_NUMBERS:,}); "
                             "use a coarser step or plot fewer points")
        out.append({"name": c.name, "label": tex(c.label or c.name), "format": c.format, "settings": values, "index": index,
                    "diffs": diffs})
    return out
