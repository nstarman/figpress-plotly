from pathlib import Path
import json
import re

import pytest
from plotly.offline import get_plotlyjs_version

from figpress_plotly import __version__

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from figpress_plotly.cli import load

    figure = load(f"{EXAMPLE / 'figure.py'}:bands")
    out = tmp_path_factory.mktemp("web")
    figure.write_web(out / "bands", single_file=out / "bands.html")
    return out


def test_the_folder(built):
    d = built / "bands"
    names = sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())
    assert names == sorted(["figure.json", "index.html", "fonts/fp-bold.ttf", "fonts/fp-math-it.ttf", "fonts/fp-math-rm.ttf",
                            "fonts/fp-text.ttf", f"vendor/figpress-plotly-{__version__}/index.js",
                            f"vendor/plotly-{get_plotlyjs_version()}.min.js"])
    page = (d / "index.html").read_text()
    assert f'<meta name="figpress-plotly-version" content="{__version__}">' in page


def test_the_spec(built):
    s = json.loads((built / "bands" / "figure.json").read_text())
    assert s["name"] == "bands" and s["page"] == [244.8, 205.2]
    assert s["fonts"]["fp-text"] == "fonts/fp-text.ttf"
    assert s["figure"]["layout"]["hovermode"] == "closest"  # the web target
    groups = {t.get("legendgroup") for t in s["figure"]["data"]}
    assert groups == {"s1", "s2", "s3", "s5"}


@pytest.mark.parametrize("page", ["bands/index.html", "bands.html"])
def test_nothing_from_another_host(built, page):
    # The page's own references (Plotly.js's code mentions URLs it never loads here; the smoke tests
    # check what the browser actually requests).
    text = re.sub(r"(<script[^>]*>).*?(</script>)", r"\1\2", (built / page).read_text(), flags=re.S)
    urls = re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+)', text) + re.findall(r'(?:url\(|fetch\()\s*["\']?(https?://[^"\')]+)', text)
    assert not [u for u in urls if re.match(r"(https?:)?//", u)], urls


def test_the_single_file_holds_everything(built):
    text = (built / "bands.html").read_text()
    assert "data:font/ttf;base64," in text and "mount(document.getElementById" in text
    assert "<script src=" not in text and "fetch(" not in text.split("mount(document")[1]
