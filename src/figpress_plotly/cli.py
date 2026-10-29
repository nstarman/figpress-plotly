"""figpress-plotly build | compare."""

import argparse
import importlib.util
import sys
from pathlib import Path

from .compare import compare
from .figure import Figure


def load(spec: str) -> Figure:
    """`path/to/file.py:name` → the Figure it defines."""
    file, _, name = spec.rpartition(":")
    if not file or not name:
        raise SystemExit(f"expected FILE.py:NAME, not {spec!r}")
    mod_spec = importlib.util.spec_from_file_location(Path(file).stem, file)
    if mod_spec is None:
        raise SystemExit(f"cannot load {file}")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    fig = getattr(mod, name, None)
    if not isinstance(fig, Figure):
        raise SystemExit(f"{name!r} in {file} is not a figure (decorate it with @fp.figure)")
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="figpress-plotly")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="write a figure's PDF and web page")
    b.add_argument("figure", help="FILE.py:NAME")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--target", choices=("pdf", "web", "both"), default="both")
    c = sub.add_parser("compare", help="measure a PDF against a reference PDF")
    c.add_argument("new", type=Path)
    c.add_argument("reference", type=Path)
    c.add_argument("--tol", type=float, default=1.0, help="pt (default 1)")
    c.add_argument("--overlay", type=Path)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "build":
            fig = load(args.figure)
            if args.target in ("pdf", "both"):
                print(fig.write_pdf(args.out / f"{fig.name}.pdf"))
            if args.target in ("web", "both"):
                print(fig.write_web(args.out / fig.name, single_file=args.out / f"{fig.name}.html"))
            return 0
        result = compare(args.new, args.reference, tol=args.tol, overlay=args.overlay)
        print(result.report())
        return 0 if result.ok else 1
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        print(f"figpress-plotly: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
