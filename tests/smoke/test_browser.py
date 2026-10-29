"""The web figure in a browser: hover, legend toggles, resize, offline (US2)."""

import re

import pytest

pytestmark = pytest.mark.smoke

GROUP_VISIBLE = """g => document.getElementById('figure').data
  .filter(t => t.legendgroup === g).map(t => t.visible === 'legendonly' ? 'hidden' : 'shown')"""
ENTRY_OPACITY = """g => document.getElementById('figure').layout.annotations
  .find(a => a.name === 'legend:' + g).opacity ?? 1"""


def legend_label(page, text):
    """The centre of the legend label reading `text`, in page px."""
    box = page.evaluate("""t => {
      for (const g of document.querySelectorAll('#figure .annotation'))
        if (g.textContent.replace(/\\s/g, '') === t) { const r = g.querySelector('text').getBoundingClientRect();
          return [r.x + r.width / 2, r.y + r.height / 2]; }
    }""", text)
    assert box, f"no legend label {text!r}"
    return box


def test_loads_offline_without_errors(open_page, server):
    page = open_page()
    hosts = {re.match(r"(\w+:)(//[^/]*)?", u).group(0) for u in page.requests}
    assert hosts <= {server, "data:"}, hosts
    assert not page.errors, page.errors
    assert page.evaluate("document.fonts.check('8px fp-text') && document.fonts.check('8px fp-math-it')")


def test_hover_shows_the_line_values(open_page):
    page = open_page()
    x, y = page.evaluate("""() => {
      const gd = document.getElementById('figure'), i = gd.data.findIndex(t => t.name === '2σ');
      const pt = gd.calcdata[i][200], xa = gd._fullLayout.xaxis, ya = gd._fullLayout.yaxis, r = gd.getBoundingClientRect();
      return [r.x + xa._offset + xa.c2p(pt.x), r.y + ya._offset + ya.c2p(pt.y)];
    }""")
    page.mouse.move(x - 20, y - 20)
    page.mouse.move(x, y, steps=10)  # Plotly hovers on mouse moves, which a jump skips
    page.wait_for_selector(".hoverlayer .hovertext")
    text = page.text_content(".hoverlayer .hovertext")  # SVG, so no inner_text
    assert "2σ" in text and "N =" in text and "r = 0.50" in text


def test_a_legend_entry_toggles_its_group_and_survives_resize(open_page):
    page = open_page(width=500)
    page.mouse.click(*legend_label(page, "1σ"))
    page.wait_for_function(f"({GROUP_VISIBLE})('s1').every(v => v === 'hidden')")
    assert page.evaluate(GROUP_VISIBLE, "s2") == ["shown"] * 3
    assert page.evaluate(ENTRY_OPACITY, "s1") == pytest.approx(0.35)
    width = page.evaluate("document.getElementById('figure')._fullLayout.width")
    page.set_viewport_size({"width": 400, "height": 900})
    page.wait_for_function(f"document.getElementById('figure')._fullLayout.width < {width}")
    assert page.evaluate(GROUP_VISIBLE, "s1") == ["hidden"] * 3
    page.mouse.click(*legend_label(page, "1σ"))
    page.wait_for_function(f"({GROUP_VISIBLE})('s1').every(v => v === 'shown')")


def test_the_single_file_works_from_disk(open_page, example):
    out, _ = example
    page = open_page(url=(out / "bands.html").as_uri())
    assert not page.errors, page.errors
    assert {re.match(r"\w+:", u).group(0) for u in page.requests} <= {"file:", "data:"}
    assert page.evaluate("document.fonts.check('8px fp-text')")


def test_plotly_legend_clicks_survive_resize(open_page, server):
    """The native example uses Plotly's own legend (US6)."""
    page = open_page(width=500, url=f"{server}/rotation/index.html")
    state = "n => document.getElementById('figure').data.find(t => t.name === n).visible ?? true"
    box = page.evaluate("""() => {
      for (const g of document.querySelectorAll('#figure .legend .traces'))
        if (g.textContent.trim() === 'Disk') { const r = g.querySelector('.legendtoggle').getBoundingClientRect();
          return [r.x + r.width / 2, r.y + r.height / 2]; }
    }""")
    page.mouse.click(*box)
    page.wait_for_function(f"({state})('Disk') === 'legendonly'")
    assert page.evaluate(state, "Halo") is True
    width = page.evaluate("document.getElementById('figure')._fullLayout.width")
    page.set_viewport_size({"width": 400, "height": 900})
    page.wait_for_function(f"document.getElementById('figure')._fullLayout.width < {width}")
    assert page.evaluate(state, "Disk") == "legendonly"


def test_a_narrow_column_scrolls_rather_than_shrinking_past_half(open_page):
    """Edge case: below half the print width the figure keeps that size and the column scrolls."""
    page = open_page(width=120)
    width = page.evaluate("document.getElementById('figure')._fullLayout.width")
    assert width == round(244.8 * 4 / 3 * 0.5)
    assert page.evaluate("(e => e.scrollWidth > e.clientWidth)(document.getElementById('figure'))")
