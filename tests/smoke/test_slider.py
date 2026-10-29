"""A control on the web: the slider puts in the values built for each setting (US3)."""

import pytest

pytestmark = pytest.mark.smoke

# Every trace's y at point 200, from what Plotly drew.
YS = "() => document.getElementById('figure').calcdata.map(c => c[200] && c[200].y)"
SET = """i => { const s = document.querySelector('.fp-control input'); s.value = i;
  s.dispatchEvent(new Event('input', { bubbles: true })); }"""


def test_the_slider_moves_only_the_lines(open_page):
    page = open_page(width=500)
    assert page.text_content(".fp-control output") == "0.50"  # the paper's value
    assert "r" in page.text_content(".fp-control span")
    before = page.evaluate(YS)
    names = page.evaluate("document.getElementById('figure').data.map(t => t.name || '')")
    page.evaluate(SET, 9)  # 0.12 + 9 × 0.02
    page.wait_for_function(f"({YS})()[{names.index('2σ')}] !== {before[names.index('2σ')]}")
    assert page.text_content(".fp-control output") == "0.30"
    after = page.evaluate(YS)
    for name, b, a in zip(names, before, after):
        if name.endswith("σ"):  # the lines follow r
            assert a != pytest.approx(b, rel=1e-3), name
        else:  # the bands (over r's range) do not
            assert a == pytest.approx(b, rel=1e-6), name


def test_hover_follows_and_a_resize_keeps_the_setting(open_page):
    page = open_page(width=500)
    page.evaluate(SET, 9)
    page.wait_for_function("document.getElementById('figure').data.some(t => (t.hovertemplate || '').includes('r = 0.30'))")
    x, y = page.evaluate("""() => {
      const gd = document.getElementById('figure'), i = gd.data.findIndex(t => t.name === '2σ');
      const pt = gd.calcdata[i][200], xa = gd._fullLayout.xaxis, ya = gd._fullLayout.yaxis, r = gd.getBoundingClientRect();
      return [r.x + xa._offset + xa.c2p(pt.x), r.y + ya._offset + ya.c2p(pt.y)];
    }""")
    page.mouse.move(x - 20, y - 20)
    page.mouse.move(x, y, steps=10)
    page.wait_for_selector(".hoverlayer .hovertext")
    assert "r = 0.30" in page.text_content(".hoverlayer .hovertext")
    width = page.evaluate("document.getElementById('figure')._fullLayout.width")
    page.set_viewport_size({"width": 400, "height": 900})
    page.wait_for_function(f"document.getElementById('figure')._fullLayout.width < {width}")
    assert page.evaluate("document.getElementById('figure').data.some(t => (t.hovertemplate || '').includes('r = 0.30'))")
    assert page.input_value(".fp-control input") == "9"
