from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


@pytest.fixture(scope="session")
def example_pdf(tmp_path_factory):
    """The example built for print once per run (it takes a few seconds: Chrome)."""
    from figpress_plotly.cli import load

    figure = load(f"{EXAMPLE / 'figure.py'}:bands")
    return figure.write_pdf(tmp_path_factory.mktemp("bands") / "bands.pdf"), figure
