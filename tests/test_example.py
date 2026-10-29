"""The example's print figure matches its matplotlib reference within 1 pt (SC-001)."""

from conftest import EXAMPLE

from figpress_plotly import compare


def test_matches_the_reference(example_pdf, tmp_path):
    path, _ = example_pdf
    result = compare(path, EXAMPLE / "reference.pdf", tol=1.0, overlay=tmp_path / "overlay.png")
    assert result.ok, result.report()
    assert len([e for e in result.elements if e.kind == "frame"]) == 4
