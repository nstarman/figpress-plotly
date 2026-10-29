import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


@pytest.fixture(scope="session")
def example_pdf(tmp_path_factory):
    """The example built for print once per run (it takes a few seconds: Chrome)."""
    sys.path.insert(0, str(EXAMPLE))
    import figure

    return figure.bands.write_pdf(tmp_path_factory.mktemp("bands") / "bands.pdf"), figure.bands
