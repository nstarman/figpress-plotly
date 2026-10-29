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

/** The figure as the reader left it: hidden groups' traces invisible, their legend entries dimmed. */
export function applyState(figure, state) {
  const data = figure.data.map((t) => (state.hidden.has(t.legendgroup) ? { ...t, visible: false } : t));
  const dim = (o) => (state.hidden.has(groupOf(o.name)) ? { ...o, opacity: DIM } : o);
  const layout = { ...figure.layout, shapes: (figure.layout.shapes ?? []).map(dim),
    annotations: (figure.layout.annotations ?? []).map(dim) };
  return { data, layout };
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
  const state = { hidden: new Set() };
  const base = spec.figure;
  const printWidth = base.layout.width;
  const draw = () => {
    const s = fitScale(el.clientWidth || printWidth, printWidth);
    const { data, layout } = applyState(base, state);
    return Plotly.react(el, scaleLayout(data, s), roundGeometry(scaleLayout(layout, s)), { displayModeBar: false, responsive: false });
  };
  await draw();
  let pending;
  new ResizeObserver(() => { clearTimeout(pending); pending = setTimeout(draw, 50); }).observe(el);
  // A legend entry's label toggles its group (its traces; its handle and label dim).
  el.addEventListener("click", (e) => {
    const g = e.target.closest(".annotation");
    const ann = g && el.layout.annotations[+g.dataset.index];
    const group = ann && groupOf(ann.name);
    if (!group) return;
    state.hidden.has(group) ? state.hidden.delete(group) : state.hidden.add(group);
    draw();
  });
  return { state, draw };
}
