import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
test("bundled legal pages match their draft source files", () => {
  const legal = JSON.parse(
    fs.readFileSync(new URL("../content/legal.json", import.meta.url), "utf8"),
  );
  for (const kind of ["privacy", "terms"]) {
    assert.equal(
      legal[kind],
      fs.readFileSync(
        new URL(`../content/${kind}.md`, import.meta.url),
        "utf8",
      ),
    );
    assert.ok(legal[kind].includes("Draft — pending legal review."));
  }
});
