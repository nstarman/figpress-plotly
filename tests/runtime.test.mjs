// The runtime's pure functions: scaling and the reader's state.
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyState, darken, darkLayout, darkNeutral, DARK, fitScale, formatValue, isDark, roundGeometry, scaleLayout, setPath, traceGroup } from "../src/figpress_plotly/js/index.js";

test("pixel settings scale; data and other numbers do not", () => {
  const layout = { width: 300, margin: { l: 40, t: 2, pad: 0 }, font: { size: 10 }, xaxis: { range: [-3, -1], ticklen: 4,
    ticklabelstandoff: 3, title: { standoff: 5 } }, shapes: [{ x0: 0.5, line: { width: 1, dash: "1.00px,1.65px" } }],
    annotations: [{ x: 0.2, yshift: 3, font: { size: 8 } }] };
  const s = scaleLayout(layout, 2);
  assert.equal(s.width, 600);
  assert.deepEqual(s.margin, { l: 80, t: 4, pad: 0 });
  assert.deepEqual(s.xaxis.range, [-3, -1]);
  assert.equal(s.xaxis.ticklen, 8);
  assert.equal(s.xaxis.ticklabelstandoff, 6);
  assert.equal(s.xaxis.title.standoff, 10);
  assert.equal(s.shapes[0].x0, 0.5);
  assert.equal(s.shapes[0].line.dash, "2.00px,3.30px");
  assert.equal(s.annotations[0].yshift, 6);
  assert.equal(scaleLayout({ ticklabelstandoff: 3 }, 0.5).ticklabelstandoff, 2); // whole px
});

test("typed arrays are data", () => {
  const t = { y: { dtype: "f8", bdata: "AAAA" }, line: { width: 2 } };
  assert.deepEqual(scaleLayout(t, 3), { y: { dtype: "f8", bdata: "AAAA" }, line: { width: 6 } });
});

test("a hidden group: its traces invisible, its legend entry dimmed, the rest untouched", () => {
  const fig = { data: [{ legendgroup: "s1" }, { legendgroup: "s2" }],
    layout: { shapes: [{ name: "legend:s1" }, { name: "other" }], annotations: [{ name: "legend:s1" }, { name: "legend:s2" }] } };
  const { data, layout } = applyState(fig, { hidden: new Set(["s1"]) });
  assert.equal(data[0].visible, "legendonly");
  assert.equal(data[1].visible, undefined);
  assert.equal(layout.shapes[0].opacity, 0.35);
  assert.equal(layout.shapes[1].opacity, undefined);
  assert.equal(layout.annotations[1].opacity, undefined);
  assert.equal(fig.data[0].visible, undefined); // the figure itself is not changed
});

test("the fit is capped", () => {
  assert.equal(fitScale(600, 300), 2);
  assert.equal(fitScale(3000, 300), 3);
});

test("the plot area's edges are rounded, not each margin", () => {
  // edges at 22.9 and 163.2 − 6.9 = 156.3 px: rounded 23 and 156, so r = 163 − 156 = 7
  const g = roundGeometry({ width: 163.2, height: 136.8, margin: { l: 22.9, r: 6.9, t: 2.9, b: 19.4, pad: 0 } });
  assert.deepEqual([g.width, g.margin.l, g.margin.r], [163, 23, 7]);
  assert.deepEqual([g.height, g.margin.t, g.margin.b], [137, 3, 20]);
});

test("a trace without a legendgroup is its own group", () => {
  assert.equal(traceGroup({ legendgroup: "s1" }, 4), "s1");
  assert.equal(traceGroup({ name: "data" }, 4), "trace:4");
  const { data } = applyState({ data: [{ name: "a" }, { name: "b" }], layout: {} }, { hidden: new Set(["trace:1"]) });
  assert.deepEqual(data.map((t) => t.visible), [undefined, "legendonly"]);
});

test("setPath copies only along the path", () => {
  const a = { data: [{ y: [1] }, { y: [2] }], layout: { x: 1 } };
  const b = setPath(a, ["data", 1, "y"], [3]);
  assert.deepEqual(b.data[1].y, [3]);
  assert.equal(a.data[1].y[0], 2);
  assert.equal(b.data[0], a.data[0]);
  assert.equal(b.layout, a.layout);
});

const C = [{ name: "k", index: 1, settings: [0.5, 1, 1.5],
  diffs: [{ path: ["data", 0, "y"], values: [[0.5], [1], [1.5]] }, { path: ["layout", "annotations", 0, "text"], values: ["a", "b", "c"] }] }];
const FIG = { data: [{ y: [1] }], layout: { annotations: [{ text: "b" }], shapes: [] } };

test("a control at a setting puts in that setting's values", () => {
  const { data, layout } = applyState(FIG, { hidden: new Set(), controls: { k: 2 } }, C);
  assert.deepEqual(data[0].y, [1.5]);
  assert.equal(layout.annotations[0].text, "c");
});

test("at the paper's setting the figure is the paper's, untouched", () => {
  const { data } = applyState(FIG, { hidden: new Set(), controls: { k: 1 } }, C);
  assert.equal(data[0], FIG.data[0]);
});

test("a stale setting is clamped", () => {
  assert.deepEqual(applyState(FIG, { hidden: new Set(), controls: { k: 9 } }, C).data[0].y, [1.5]);
  assert.deepEqual(applyState(FIG, { hidden: new Set(), controls: { k: -3 } }, C).data[0].y, [0.5]);
});

test("readouts", () => {
  assert.equal(formatValue(0.5, ".2f"), "0.50");
  assert.equal(formatValue(0.5, "g"), "0.5");
});

test("dark: greys map between the palette's text and background; colours and alpha stay", () => {
  assert.equal(darkNeutral("white"), "rgb(11,14,20)");
  assert.equal(darkNeutral("black"), "rgb(229,233,240)");
  assert.equal(darkNeutral("#000000"), "rgb(229,233,240)");
  assert.equal(darkNeutral("rgba(128,128,128,0.4)"), "rgba(120,123,130,0.4)");
  assert.equal(darkNeutral("rgba(31,119,180,0.15)"), "rgba(31,119,180,0.15)");
  assert.equal(darkNeutral("rgb(255,0,0)"), "rgb(255,0,0)");
});

test("dark: colour settings only, backgrounds and text set", () => {
  const fig = darken({ line: { color: "black", width: 2 }, name: "black", fillcolor: "white", y: { bdata: "x", dtype: "f8" } });
  assert.deepEqual(fig, { line: { color: "rgb(229,233,240)", width: 2 }, name: "black", fillcolor: "rgb(11,14,20)",
    y: { bdata: "x", dtype: "f8" } });
  const l = darkLayout({ font: { size: 10 } });
  assert.deepEqual([l.paper_bgcolor, l.plot_bgcolor, l.font.color, l.font.size], [DARK.ground, DARK.ground, DARK.ink, 10]);
});

test("the theme: asked for, else the toggle, else the system", () => {
  const doc = (theme) => ({ documentElement: { dataset: theme ? { theme } : {} } });
  const win = (search, dark) => ({ location: { search }, matchMedia: () => ({ matches: dark }) });
  assert.equal(isDark(doc(), win("?theme=dark", false)), true);
  assert.equal(isDark(doc("dark"), win("?theme=light", true)), false);
  assert.equal(isDark(doc("dark"), win("", false)), true);
  assert.equal(isDark(doc(), win("", true)), true);
  assert.equal(isDark(doc(), win("", false)), false);
});
