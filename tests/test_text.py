import plotly.graph_objects as go
import pytest

from figpress_plotly import dejavu
from figpress_plotly.figure import Figure
from figpress_plotly.text import frac, runs, stack, tex, text, width


def test_runs_follow_mathtext():
    assert runs(r"Rate $\lambda_{\rm C}$") == [("Rate ", "text", None), ("λ", "math_italic", None),
                                                ("C", "math_upright", "sub")]
    assert runs(r"$x^2 - 1$") == [("x", "math_italic", None), ("2", "math_upright", "sup"),
                                  ("\u2005−\u20051", "math_upright", None)]
    assert runs(r"$-\mathrm{SI} \in \Gamma$") == [("−SI\u2005∈\u2005Γ", "math_upright", None)]


def test_a_script_on_the_text_before():
    assert runs(r"km s$^{-1}$") == [("km s", "text", None), ("−1", "math_upright", "sup")]


def test_tex_is_plotly_markup_in_the_paper_fonts():
    assert tex(r"a $p_{\rm A}$ & b") == ('a <span style="font-family:fp-math-it">p</span>'
                                          '<sub><span style="font-family:fp-math-rm">A</span></sub> &amp; b')


def test_unsupported_and_malformed_math_are_named():
    with pytest.raises(ValueError, match=r"\\frac"):
        tex(r"$\frac{1}{2}$")
    with pytest.raises(ValueError, match="nested"):
        tex(r"$x^{y^2}$")
    with pytest.raises(ValueError, match="braces"):
        tex(r"$x^{2$")


def build(fn):
    return Figure(fn, page=(100, 50), frame=(10, 5, 80, 40), fonts=dejavu(), spine=0).build("pdf")


def test_text_places_the_baseline():
    fig = build(lambda target: (f := go.Figure(), text(f, "Hi", 10, 25, 8), f)[2])
    a = fig.layout.annotations[0]
    assert (a.xanchor, a.yanchor, a.borderpad, a.x) == ("left", "middle", 0, 0)
    # DejaVu Serif: ascent 0.928, descent 0.236 em → the middle 0.346 em above the baseline, and Chrome drops it 0.123 em
    assert a.y == pytest.approx(1 - (25 - (0.346 + 0.123) * 8 - 5) / 40, abs=1e-3)


def test_stack_puts_scripts_after_the_base():
    def fn(target):
        f = go.Figure()
        stack(f, "$p$", r"$\rm sim$", r"$\rm A$", 50, 20, 7)
        assert width("$p$", 7) == pytest.approx(0.6 * 7, rel=0.1)
        return f
    base, sup, sub = build(fn).layout.annotations
    assert sup.x == sub.x > base.x and sup.y > base.y > sub.y and sup.font.size == pytest.approx(7 * 0.7 * 4 / 3)


def test_frac_draws_a_bar_between():
    def fn(target):
        f = go.Figure()
        frac(f, r"$\lambda_{\rm SI}$", r"$\lambda_{\rm C}$", 50, 25, 7)
        return f
    fig = build(fn)
    num, den = fig.layout.annotations
    bar = fig.layout.shapes[0]
    assert num.y > bar.y0 > den.y and bar.x0 < num.x < bar.x1
