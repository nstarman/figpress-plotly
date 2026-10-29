"""Smoke tests drive the built example in a real browser: `uv run pytest -m smoke`."""

import functools
import http.server
import sys
import threading
from pathlib import Path

import pytest

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "bands"


@pytest.fixture(scope="session")
def example(tmp_path_factory):
    sys.path.insert(0, str(EXAMPLE))
    import figure

    out = tmp_path_factory.mktemp("smoke")
    figure.bands.write_pdf(out / "bands.pdf")
    figure.bands.write_web(out / "bands", single_file=out / "bands.html")
    return out, figure.bands


@pytest.fixture(scope="session")
def server(example):
    out, _ = example
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    handler.log_message = lambda *a: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def open_page(browser, server):
    """Open the folder page (or a given URL) at a viewport width; record every request and console error."""
    pages = []

    def go(width=327, url=None, scale=1):
        page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=scale)
        page.requests, page.errors = [], []
        page.on("request", lambda r: page.requests.append(r.url))
        page.on("console", lambda m: m.type == "error" and page.errors.append(m.text))
        page.on("pageerror", lambda e: page.errors.append(str(e)))
        page.goto(url or f"{server}/bands/index.html")
        page.wait_for_function("document.querySelector('#figure .main-svg') && document.getElementById('figure')._fullLayout")
        pages.append(page)
        return page

    yield go
    for p in pages:
        p.close()
