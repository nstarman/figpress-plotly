"""The web figure: a page folder, and the same page as one self-contained HTML file. Nothing is loaded
from another host: Plotly.js, the runtime and the fonts are included at their versions."""

import html
import json
import shutil
from pathlib import Path

from plotly.offline import get_plotlyjs, get_plotlyjs_version

from . import __version__
from .controls import pack
from .fonts import b64

RUNTIME = Path(__file__).parent / "js" / "index.js"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="figpress-plotly-version" content="{version}">
<title>{title}</title>
<style>
html, body {{ margin: 0; background: #fff; color: #12161c; }} .fp-figure {{ width: 100%; }}
html:has(.fp-figure[data-theme="dark"]), html:has(.fp-figure[data-theme="dark"]) body {{
  background: #0b0e14; color: #e5e9f0; color-scheme: dark;
}}
</style>
{plotly}
</head>
<body>
<div class="fp-figure" id="figure"></div>
{boot}
</body>
</html>
"""


def spec(figure, fonts: dict[str, str], **params) -> dict:
    """What the runtime draws: the web figure, its controls and where its fonts are."""
    base = json.loads(figure.build("web", **params).to_json())
    return {"version": __version__, "name": figure.name, "page": list(figure.page),
            "figure": base, "fonts": fonts, "controls": pack(figure, base, **params)}



def write_web(figure, out: Path, single_file: Path | None = None, **params) -> Path:
    """Write the page folder `out` (index.html, figure.json, fonts/, vendor/); with `single_file`,
    also the page as one HTML file. Returns `out`."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "fonts").mkdir(parents=True)
    files = figure.fonts.files()
    for family, path in files.items():
        shutil.copyfile(path, out / "fonts" / f"{family}{path.suffix}")
    s = spec(figure, {fam: f"fonts/{fam}{p.suffix}" for fam, p in files.items()}, **params)
    (out / "figure.json").write_text(json.dumps(s), encoding="utf-8")
    plotly_js = f"vendor/plotly-{get_plotlyjs_version()}.min.js"
    runtime = f"vendor/figpress-plotly-{__version__}/index.js"
    (out / runtime).parent.mkdir(parents=True)
    (out / plotly_js).write_text(get_plotlyjs(), encoding="utf-8")
    shutil.copyfile(RUNTIME, out / runtime)
    boot = (f'<script type="module">\nimport {{ mount }} from "./{runtime}";\n'
            'const spec = await (await fetch("figure.json")).json();\n'
            'mount(document.getElementById("figure"), spec);\n</script>')
    (out / "index.html").write_text(PAGE.format(version=__version__, title=html.escape(figure.name),
                                                plotly=f'<script src="{plotly_js}"></script>', boot=boot), encoding="utf-8")
    if single_file is not None:
        write_single(figure, Path(single_file), _spec=s, **params)
    return out


def write_single(figure, path: Path, _spec: dict | None = None, **params) -> Path:
    """The page as one HTML file: Plotly.js, the runtime, the figure and the fonts inlined."""
    fonts = {fam: f"data:font/ttf;base64,{b64(p)}" for fam, p in figure.fonts.files().items()}
    s = {**_spec, "fonts": fonts} if _spec is not None else spec(figure, fonts, **params)
    s = json.dumps(s).replace("</", "<\\/")
    # The runtime's own module, inlined; its exports are unused here.
    boot = (f'<script type="module">\n{RUNTIME.read_text(encoding="utf-8")}\n'
            f'mount(document.getElementById("figure"), {s});\n</script>')
    plotly = f"<script>{get_plotlyjs()}</script>"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PAGE.format(version=__version__, title=html.escape(figure.name), plotly=plotly, boot=boot),
                    encoding="utf-8")
    return path
