"""A new figure, native from the start: built from a style and margins, with no reference (US6)."""

import re
from pathlib import Path

import pypdfium2 as pdfium
import pytest

from figpress_plotly.cli import load
from figpress_plotly.compare import _lines, _render

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "examples" / "native"


@pytest.fixture(scope="module")
def native(tmp_path_factory):
    fig = load(f"{NATIVE / 'figure.py'}:rotation")  # both examples have a figure.py: no import by name
    return fig.write_pdf(tmp_path_factory.mktemp("native") / "rotation.pdf"), fig


def test_the_page_and_only_the_styles_fonts(native):
    path, fig = native
    assert pdfium.PdfDocument(str(path))[0].get_size() == pytest.approx((242, 170), abs=0.1)
    names = {n.split(b"+")[-1] for n in re.findall(rb"/BaseFont\s*/([A-Za-z0-9+\-_]+)", path.read_bytes())}
    assert names and all(n.startswith(b"STIXGeneral") for n in names), names


def test_the_plot_area_follows_the_margins(native):
    path, fig = native
    frame = _lines(_render(pdfium.PdfDocument(str(path))[0]))
    left, top, right, bottom = 38, 6, 242 - 8, 170 - 28  # the style's margins
    assert frame == pytest.approx({"left": left, "top": top, "right": right, "bottom": bottom}, abs=0.6)
