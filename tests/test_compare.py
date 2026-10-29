import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

from figpress_plotly import compare  # noqa: E402


def page(path, label_x=0.5, title="Hello", size=(3, 2), axes=(0.2, 0.2, 0.7, 0.7)):
    plt.rcParams["pdf.fonttype"] = 42
    fig = plt.figure(figsize=size)
    ax = fig.add_axes(axes)
    ax.set_ylabel("Rotated label")
    fig.text(label_x, 0.95, title, ha="center", va="top")
    fig.savefig(path)
    plt.close(fig)
    return path


def test_identical_pdfs_pass(tmp_path):
    a = page(tmp_path / "a.pdf")
    c = compare(a, a, overlay=tmp_path / "o.png")
    assert c.ok and (tmp_path / "o.png").exists()
    names = {e.name for e in c.elements}
    assert {"Hello", "Rotatedlabel", "left", "right", "top", "bottom"} <= names


def test_a_moved_label_fails_and_is_named(tmp_path):
    a, b = page(tmp_path / "a.pdf"), page(tmp_path / "b.pdf", label_x=0.5 + 2 / 216)  # 2 pt right
    c = compare(b, a, tol=1)
    bad = [e for e in c.elements if not e.ok]
    assert [e.name for e in bad] == ["Hello"] and bad[0].dx == pytest.approx(2, abs=0.1)
    assert compare(b, a, tol=3).ok


def test_a_missing_label_fails(tmp_path):
    a, b = page(tmp_path / "a.pdf"), page(tmp_path / "b.pdf", title="Bye")
    assert [e.name for e in compare(b, a).elements if not e.ok] == ["Hello"]


def test_the_frame_moves(tmp_path):
    a, b = page(tmp_path / "a.pdf"), page(tmp_path / "b.pdf", axes=(0.2 + 1.5 / 216, 0.2, 0.7, 0.7))
    bad = {e.name: e.dx for e in compare(b, a).elements if not e.ok and e.kind == "frame"}  # its tick labels move too
    assert set(bad) == {"left", "right"} and bad["left"] == pytest.approx(1.5, abs=0.15)


def test_page_sizes_must_agree(tmp_path):
    with pytest.raises(ValueError, match="page sizes differ"):
        compare(page(tmp_path / "a.pdf"), page(tmp_path / "b.pdf", size=(3, 2.5)))
