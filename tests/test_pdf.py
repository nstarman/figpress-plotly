import pypdfium2 as pdfium
import pytest

from figpress_plotly import pdf


def test_one_page_at_exactly_the_page_size(example_pdf):
    path, fig = example_pdf
    doc = pdfium.PdfDocument(str(path))
    assert len(doc) == 1
    assert doc[0].get_size() == pytest.approx(fig.page, abs=0.1)


def test_only_the_given_fonts_embedded(example_pdf):
    path, fig = example_pdf
    data = path.read_bytes()
    names = {n.split(b"+")[-1] for n in __import__("re").findall(rb"/BaseFont\s*/([A-Za-z0-9+\-_]+)", data)}
    assert names and names <= {b"DejaVuSerif", b"DejaVuSerif-Bold", b"DejaVuSans", b"DejaVuSans-Oblique"}, names
    assert b"/FontFile2" in data  # embedded TrueType


def test_no_chrome_is_a_clear_error(monkeypatch):
    from choreographer.browsers import chromium

    monkeypatch.setattr(chromium.Chromium, "find_browser", staticmethod(lambda **kw: None))
    with pytest.raises(RuntimeError, match="no Chrome"):
        pdf.chrome()
