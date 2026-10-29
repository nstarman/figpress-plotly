from pathlib import Path

from figpress_plotly.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "bands"


def test_build_writes_the_pdf(tmp_path, capsys):
    assert main(["build", f"{EXAMPLE / 'figure.py'}:bands", "--out", str(tmp_path), "--target", "pdf"]) == 0
    assert (tmp_path / "bands.pdf").exists()


def test_build_needs_a_figure(tmp_path):
    bad = tmp_path / "f.py"
    bad.write_text("x = 1\n")
    try:
        main(["build", f"{bad}:x", "--out", str(tmp_path)])
    except SystemExit as e:
        assert "not a figure" in str(e)
    else:
        raise AssertionError("expected an error")


def test_compare_exit_codes(example_pdf, capsys):
    path, _ = example_pdf
    assert main(["compare", str(path), str(EXAMPLE / "reference.pdf")]) == 0
    assert "all within 1 pt" in capsys.readouterr().out
    assert main(["compare", str(path), str(EXAMPLE / "reference.pdf"), "--tol", "0.05"]) == 1
