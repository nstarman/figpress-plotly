"""Light and dark (US5): neutral colours follow the theme, data colours do not."""

import pytest

pytestmark = pytest.mark.smoke

FULL = """() => { const gd = document.getElementById('figure'), fl = gd._fullLayout;
  return { paper: fl.paper_bgcolor, axis: fl.xaxis.linecolor, tick: fl.xaxis.tickfont.color,
           line: gd._fullData.find(t => t.name === '2σ').line.color,
           body: getComputedStyle(document.body).backgroundColor }; }"""
LIGHT = {"paper": "white", "axis": "black", "tick": "black"}


def test_dark_when_asked(open_page, server):
    page = open_page(url=f"{server}/bands/index.html?theme=dark")
    light = open_page(url=f"{server}/bands/index.html?theme=light")
    d, l = page.evaluate(FULL), light.evaluate(FULL)
    assert d["paper"] == "rgb(11,14,20)" and d["axis"] == "rgb(229,233,240)" and d["tick"] == "rgb(229,233,240)"
    assert d["line"] == l["line"]  # the data's colour stays the paper's
    assert d["body"] == "rgb(11, 14, 20)" and l["body"] == "rgb(255, 255, 255)"
    assert {k: l[k] for k in LIGHT} == LIGHT


def test_follows_the_websites_toggle(open_page):
    page = open_page()
    paper = "document.getElementById('figure')._fullLayout.paper_bgcolor"
    page.evaluate("document.documentElement.dataset.theme = 'dark'")
    page.wait_for_function(f"{paper} === 'rgb(11,14,20)'")
    page.evaluate("document.documentElement.dataset.theme = 'light'")
    page.wait_for_function(f"{paper} === 'white'")


def test_follows_the_system(browser, server):
    page = browser.new_page(color_scheme="dark")
    page.goto(f"{server}/bands/index.html")
    page.wait_for_function("document.getElementById('figure')._fullLayout?.paper_bgcolor === 'rgb(11,14,20)'")
    page.emulate_media(color_scheme="light")
    page.wait_for_function("document.getElementById('figure')._fullLayout.paper_bgcolor === 'white'")
    page.close()
