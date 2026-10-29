// The runtime's pure functions: scaling and the reader's state.
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyState, fitScale, roundGeometry, scaleLayout } from "../src/figpress_plotly/js/index.js";

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
  assert.equal(data[0].visible, false);
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
