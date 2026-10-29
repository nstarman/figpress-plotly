"""figpress-plotly: a paper's figures in Plotly, in print and on the web.

In early development. A figure is one ``build(target)`` that gives both the print PDF the paper
publishes and a matching interactive web figure. Follow it at
https://github.com/nstarman/figpress-plotly and the figpress family at https://nstarkman.space/figpress/.
"""

from .compare import compare
from .figure import Control, Figure, context, figure
from .fonts import Fonts, dejavu
from .legend import Entry, legend
from .style import Style
from .text import frac, stack, tex, text
from .units import dash, pt

__all__ = ("Control", "Entry", "Figure", "Fonts", "Style", "__version__", "compare", "context", "dash", "dejavu", "figure",
           "frac", "legend", "pt", "stack", "tex", "text")

__version__ = "2026.10.28"
