# Contract: CLI

```bash
figpress-plotly build examples/bands/figure.py:bands --out build/   # bands.pdf, bands/, bands.html
figpress-plotly build figures.py:rate --out build/ --target pdf      # only the PDF
figpress-plotly compare build/bands.pdf examples/bands/reference.pdf --tol 1 --overlay build/overlay.png
```

- `build FILE:NAME --out DIR [--target pdf|web|both]`: exit 0 on success; 1 with the error
  otherwise.
- `compare NEW REF [--tol PT] [--overlay PNG]`: prints one line per element (`name dx dy ok`);
  exit 0 when every element is within `--tol`, 1 otherwise.
