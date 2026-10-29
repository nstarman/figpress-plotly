"""The print figure: Plotly → SVG (Kaleido, the paper's fonts in its page) → PDF printed by Chrome at
exactly the page size. Kaleido's own PDF adds a margin and cannot use the page's fonts."""

import atexit
import json
import subprocess
import tempfile
from pathlib import Path

import kaleido
import pypdfium2 as pdfium
import plotly.graph_objects as go

from .fonts import Fonts, b64


def chrome() -> str:
    """The Chrome or Chromium Kaleido uses."""
    from choreographer.browsers.chromium import Chromium

    path = Chromium.find_browser(skip_local=False)
    if not path:
        raise RuntimeError("no Chrome or Chromium found: install one, or run `plotly_get_chrome` (Kaleido's) to fetch it")
    return path


def _font_script(fonts: Fonts, path: Path) -> Path:
    """A script registering the fonts as binary FontFaces, so they are ready before Plotly measures text."""
    data = {fam: b64(f) for fam, f in fonts.files().items()}
    path.write_text("(()=>{const D=" + json.dumps(data) + ";for(const [n,b] of Object.entries(D)){"
                    "const f=new FontFace(n,Uint8Array.from(atob(b),c=>c.charCodeAt(0)).buffer);"
                    "document.fonts.add(f);f.load();}})();\n", encoding="utf-8")
    return path


_server: dict = {}  # the running Kaleido server: its fonts and its script's directory


def _kaleido(fonts: Fonts) -> None:
    """One Kaleido browser for every figure with these fonts (starting one per figure costs seconds,
    most of it its shutdown); restarted for other fonts, stopped when Python exits."""
    if _server.get("fonts") == fonts:
        return
    if _server:
        kaleido.stop_sync_server(silence_warnings=True)
        _server["tmp"].cleanup()
    tmp = tempfile.TemporaryDirectory()
    page = kaleido.PageGenerator(others=[_font_script(fonts, Path(tmp.name) / "fonts.js").as_uri()], mathjax=False)
    kaleido.start_sync_server(page_generator=page, silence_warnings=True)
    if not _server:
        atexit.register(lambda: _server and kaleido.stop_sync_server(silence_warnings=True))
    _server.update(fonts=fonts, tmp=tmp)


def svg(fig: go.Figure, fonts: Fonts) -> str:
    _kaleido(fonts)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "fig.svg"
        kaleido.write_fig_sync(fig, path=str(out), opts={"format": "svg"})
        return out.read_text(encoding="utf-8")


def write_pdf(fig: go.Figure, path: Path, page: tuple[float, float], fonts: Fonts) -> Path:
    """Write `fig` as a one-page PDF of `page` (pt), with no margin and the fonts embedded."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = page
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "print.html"
        html.write_text(f"<!doctype html><meta charset=utf-8><style>{fonts.css()}"
                        f"@page{{size:{w}pt {h}pt;margin:0}}html,body{{margin:0}}svg{{display:block}}</style>"
                        + svg(fig, fonts), encoding="utf-8")
        r = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-sandbox",
                            "--virtual-time-budget=3000", f"--print-to-pdf={path.resolve()}", html.as_uri()],
                           capture_output=True, text=True)
    # Chrome can fail on its way out after writing the PDF: judge by the PDF, not the exit code.
    try:
        _exact_page(path, w, h)
    except Exception:
        raise RuntimeError(f"Chrome could not print the figure (exit {r.returncode}):\n{r.stderr[-2000:]}") from None
    return path


def _exact_page(path: Path, w: float, h: float) -> None:
    """Chrome snaps the page to its own grid (a few tenths of a point off); set it to exactly w × h,
    keeping the content where it is from the top left."""
    doc = pdfium.PdfDocument(str(path))
    page = doc[0]
    top = page.get_mediabox()[3]
    page.set_mediabox(0, top - h, w, top)
    page.set_cropbox(0, top - h, w, top)
    tmp = path.with_suffix(".tmp.pdf")
    doc.save(str(tmp))
    doc.close()
    tmp.replace(path)
