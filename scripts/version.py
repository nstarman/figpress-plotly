"""Release versions: a tag `vYYYY.MM.DD[.N]` and the versions it publishes.

PyPI takes the tag's date as is (`YYYY.MM.DD[.N]`). npm needs three-part semver, so it gets
`YYYYMMDD.0.N`, with N = 0 for the day's first release (as the nstarkman.space packages do).

    python scripts/version.py v2026.10.28          print {"pypi": ..., "npm": ...}
    python scripts/version.py check [TAG]          exit 1 unless the Python and npm versions match
                                                   TAG (default: the tag the Python version names)
    python scripts/version.py set TAG              write both versions
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"^v(\d{4})\.(\d{2})\.(\d{2})(?:\.(\d+))?$")
PY_VERSION = re.compile(r'^__version__ = "([^"]+)"$', re.M)
JS_VERSION = re.compile(r'^export const version = "([^"]+)";$', re.M)  # the runtime, if it states one


def versions(tag: str) -> dict[str, str]:
    """The PyPI and npm versions a tag publishes."""
    m = TAG.match(tag)
    if not m:
        raise ValueError(f"{tag!r} is not a release tag vYYYY.MM.DD or vYYYY.MM.DD.N")
    year, month, day, n = m.groups()
    if n is not None and int(n) < 2:
        raise ValueError(f"{tag!r}: a same-day release number starts at 2")
    suffix = f".{int(n)}" if n else ""
    return {"pypi": f"{year}.{month}.{day}{suffix}", "npm": f"{year}{month}{day}.0.{int(n or 0)}"}


def init_file() -> Path:
    return next((ROOT / "src").glob("*/__init__.py"))


def current() -> dict[str, str]:
    """The versions the repository's files say."""
    py = PY_VERSION.search(init_file().read_text(encoding="utf-8")).group(1)
    npm = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    js = ROOT / "src/figpress_plotly/js/index.js"
    if js.exists() and (m := JS_VERSION.search(js.read_text(encoding="utf-8"))) and m.group(1) != npm:
        npm = f"{npm} (index.js says {m.group(1)})"
    return {"pypi": py, "npm": npm}


def set_versions(tag: str) -> None:
    want = versions(tag)
    init = init_file()
    init.write_text(PY_VERSION.sub(f'__version__ = "{want["pypi"]}"', init.read_text(encoding="utf-8")), encoding="utf-8")
    pkg = ROOT / "package.json"
    data = json.loads(pkg.read_text(encoding="utf-8"))
    data["version"] = want["npm"]
    pkg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    js = ROOT / "src/figpress_plotly/js/index.js"
    if js.exists():
        js.write_text(JS_VERSION.sub(f'export const version = "{want["npm"]}";', js.read_text(encoding="utf-8")), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) >= 1 and argv[0] == "set" and len(argv) == 2:
        set_versions(argv[1])
        print(json.dumps(versions(argv[1])))
        return 0
    if argv[:1] == ["check"]:
        have = current()
        tag = argv[1] if len(argv) == 2 else f"v{have['pypi']}"
        want = versions(tag)
        if have != want:
            print(f"versions {have} do not match tag {tag} (expected {want})", file=sys.stderr)
            return 1
        print(f"ok: {tag} → {want}")
        return 0
    if len(argv) == 1:
        print(json.dumps(versions(argv[0])))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
