"""At half, once and twice the print width the web figure overlays its PDF (SC-002): within 1 pt of
the print figure, or about a screen pixel where that is larger — at half width a pixel is 1.5 pt,
and Plotly lays out in whole pixels and snaps hairlines (the 0.7 pt spine is under half a pixel
there) to them."""

import io

import numpy as np
import pypdfium2 as pdfium
import pytest
from numpy.fft import fft2, ifft2
from PIL import Image

from figpress_plotly.compare import _lines

pytestmark = pytest.mark.smoke
PX = 4 / 3
GRID = 4  # blocks per side, each matched on its own


def shift(a: np.ndarray, b: np.ndarray) -> tuple[int, int]:
    """How far `a` is moved from `b` (rows, columns), by cross-correlation."""
    A, B = 255.0 - a, 255.0 - b
    A, B = A - A.mean(), B - B.mean()
    c = np.real(ifft2(fft2(A) * np.conj(fft2(B))))
    dy, dx = np.unravel_index(c.argmax(), c.shape)
    h, w = c.shape
    return (dy - h if dy > h // 2 else dy), (dx - w if dx > w // 2 else dx)


@pytest.mark.parametrize("factor", [0.5, 1, 2])
def test_overlays_the_pdf(open_page, example, factor):
    out, fig = example
    width = round(fig.page[0] * PX * factor)
    s = width / (fig.page[0] * PX)  # the scale the runtime uses
    dpr = max(2, round(4 / factor))
    per_pt = PX * s * dpr  # image px per print pt
    tol = max(1.0, 1.25 / (PX * s))  # 1 pt, or 1¼ screen px
    page = open_page(width=width, scale=dpr)
    web = np.asarray(Image.open(io.BytesIO(page.locator("#figure").screenshot())).convert("L"))
    paper = np.asarray(pdfium.PdfDocument(str(out / "bands.pdf"))[0].render(scale=per_pt).to_pil().convert("L"))
    h, w = min(web.shape[0], paper.shape[0]), min(web.shape[1], paper.shape[1])
    web, paper = web[:h, :w], paper[:h, :w]

    frame_web, frame_paper = _lines(web, per_pt), _lines(paper, per_pt)
    assert set(frame_web) == set(frame_paper) == {"left", "right", "top", "bottom"}
    for edge in frame_paper:
        assert frame_web[edge] == pytest.approx(frame_paper[edge], abs=tol), edge

    checked = 0
    for i in range(GRID):
        for j in range(GRID):
            rows = slice(i * h // GRID, (i + 1) * h // GRID)
            cols = slice(j * w // GRID, (j + 1) * w // GRID)
            if paper[rows, cols].std() < 8:
                continue  # nearly empty: nothing to match
            dy, dx = shift(web[rows, cols], paper[rows, cols])
            assert abs(dx) / per_pt <= tol and abs(dy) / per_pt <= tol, (i, j, dx / per_pt, dy / per_pt)
            checked += 1
    assert checked >= GRID * GRID // 2
