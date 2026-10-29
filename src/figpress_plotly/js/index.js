// figpress-plotly: a paper's figures in Plotly, in print and on the web. The web runtime, shared by
// every figure: it loads the paper's fonts, draws the print layout scaled to its container, keeps
// what the reader changed across redraws, and wires the interactions the figure declares.
// https://github.com/nstarman/figpress-plotly · https://nstarkman.space/figpress/
export const version = "20261028.0.0";
export const status = "early development";

// Every layout value in CSS px, scaled with the figure (CSS zoom or transforms would break Plotly's
// pointer maths, so hover would miss).
const PX_KEYS = new Set(["size", "width", "height", "ticklen", "tickwidth", "gridwidth", "linewidth", "borderwidth",
  "standoff", "startstandoff", "ticklabelstandoff", "arrowwidth", "xshift", "yshift", "borderpad", "l", "r", "t", "b", "pad"]);
const MAX_SCALE = 3;
const DIM = 0.35; // a hidden group's legend entry

/** `v` with every pixel-valued setting times `s`. */
export function scaleLayout(v, s, key) {
  if (Array.isArray(v)) return v.map((x) => scaleLayout(x, s, key));
  if (v && typeof v === "object") {
    if ("bdata" in v) return v; // a typed array: data, never pixels
    return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, scaleLayout(x, s, k)]));
  }
  if (typeof v === "number" && PX_KEYS.has(key)) return key === "ticklabelstandoff" ? Math.round(v * s) : v * s;
  if (key === "dash" && typeof v === "string" && v.includes("px")) return v.replace(/[0-9.]+(?=px)/g, (n) => (n * s).toFixed(2));
  return v;
}

/** Whole pixels, as Plotly lays out: round the page and the plot area's edges, not each margin, so
 * no edge is more than half a pixel from where the scaled print layout puts it. */
export function roundGeometry(layout) {
  const { width, height, margin: m } = layout;
  const W = Math.round(width), H = Math.round(height);
  const l = Math.round(m.l), t = Math.round(m.t);
  const r = W - Math.round(width - m.r), b = H - Math.round(height - m.b);
  return { ...layout, width: W, height: H, margin: { ...m, l, t, r, b } };
}

const groupOf = (name) => (typeof name === "string" && name.startsWith("legend:") ? name.slice(7) : null);

/** A trace's group: its legendgroup, or the trace on its own. */
export const traceGroup = (t, i) => t.legendgroup || `trace:${i}`;

/** `obj` with the value at `path` replaced, copying only what lies along the path. */
export function setPath(obj, path, value) {
  if (!path.length) return value;
  const [k, ...rest] = path;
  const copy = Array.isArray(obj) ? [...obj] : { ...obj };
  copy[k] = setPath(obj[k], rest, value);
  return copy;
}

const clamp = (i, n) => Math.max(0, Math.min(n - 1, Math.round(i)));

/** The figure as the reader left it: each control at its setting (the values built for it put in),
 * hidden groups' traces off (still in Plotly's legend, dimmed), their drawn legend entries dimmed. */
export function applyState(figure, state, controls = []) {
  let fig = figure;
  for (const c of controls) {
    const i = clamp(state.controls?.[c.name] ?? c.index, c.settings.length);
    if (i !== c.index) for (const d of c.diffs) fig = setPath(fig, d.path, d.values[i]);
  }
  const data = fig.data.map((t, i) => (state.hidden.has(traceGroup(t, i)) ? { ...t, visible: "legendonly" } : t));
  const dim = (o) => (state.hidden.has(groupOf(o.name)) ? { ...o, opacity: DIM } : o);
  const layout = { ...fig.layout, shapes: (fig.layout.shapes ?? []).map(dim),
    annotations: (fig.layout.annotations ?? []).map(dim) };
  return { data, layout };
}

/** A control's value as its readout shows it (`.2f`, or as is). */
export function formatValue(v, format) {
  const m = /^\.(\d+)f$/.exec(format ?? "");
  return m ? v.toFixed(+m[1]) : String(v);
}

/** The scale that fits the print width into `width` px. */
export const fitScale = (width, printWidth) => Math.min(MAX_SCALE, width / printWidth);

/** Draw `spec` (a built figure's figure.json) into `el` and keep it interactive. */
export async function mount(el, spec, { Plotly = globalThis.Plotly } = {}) {
  const faces = Object.entries(spec.fonts).map(([family, src]) => new FontFace(family, `url(${src})`));
  faces.forEach((f) => document.fonts.add(f));
  await Promise.all(faces.map((f) => f.load()));
  // Glyphs placed exactly, as in print: without this, Chromium on Linux rounds small text's glyph
  // advances to whole pixels, and a 5.5 pt label grows by 2 pt.
  el.style.textRendering = "geometricPrecision";
  const controls = spec.controls ?? [];
  const state = { hidden: new Set(), controls: Object.fromEntries(controls.map((c) => [c.name, c.index])) };
  const base = spec.figure;
  const printWidth = base.layout.width;
  const draw = () => {
    const s = fitScale(el.clientWidth || printWidth, printWidth);
    const { data, layout } = applyState(base, state, controls);
    return Plotly.react(el, scaleLayout(data, s), roundGeometry(scaleLayout(layout, s)), { displayModeBar: false, responsive: false });
  };
  await draw();
  const toggle = (group) => { state.hidden.has(group) ? state.hidden.delete(group) : state.hidden.add(group); draw(); };
  // Plotly's own legend: its clicks are the reader's state too, so a redraw keeps them.
  el.on("plotly_legendclick", (ev) => { toggle(traceGroup(base.data[ev.curveNumber], ev.curveNumber)); return false; });
  el.on("plotly_legenddoubleclick", () => false);
  // A slider under the figure per control, over the settings built for it.
  let frame;
  for (const c of controls) {
    const row = document.createElement("label");
    row.className = "fp-control";
    row.style.cssText = "display:flex;align-items:center;gap:.6em;margin-top:.4em;font-family:fp-text,serif";
    row.innerHTML = `<span>${c.label}</span><input type="range" min="0" max="${c.settings.length - 1}" step="1"
      style="flex:1"><output style="min-width:3em;font-variant-numeric:tabular-nums"></output>`;
    const [input, output] = [row.querySelector("input"), row.querySelector("output")];
    const show = () => { output.textContent = formatValue(c.settings[state.controls[c.name]], c.format); };
    input.value = state.controls[c.name];
    show();
    input.addEventListener("input", () => {
      state.controls[c.name] = +input.value;
      show();
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(draw);
    });
    el.after(row);
  }
  let pending;
  new ResizeObserver(() => { clearTimeout(pending); pending = setTimeout(draw, 50); }).observe(el);
  // A legend entry's label toggles its group (its traces; its handle and label dim).
  el.addEventListener("click", (e) => {
    const g = e.target.closest(".annotation");
    const ann = g && el.layout.annotations[+g.dataset.index];
    const group = ann && groupOf(ann.name);
    if (group) toggle(group);
  });
  return { state, draw };
}
