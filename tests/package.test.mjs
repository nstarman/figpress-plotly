// The npm package imports and reports its version and status.
import { test } from "node:test";
import assert from "node:assert/strict";
import { version, status } from "../src/figpress_plotly/js/index.js";

test("version and status", () => {
  assert.match(version, /^\d{8}\.0\.\d+$/);
  assert.match(status, /early development/);
});
