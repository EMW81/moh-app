#!/usr/bin/env node
// Inject step (CLAUDE.md architecture — template-as-source):
//   index.template.html + design/tokens.css + data/pilot50.json + design/brand/build/*.png -> index.html
// The shipped index.html stays a single self-contained file; brand artwork is base64-embedded
// (assets pre-processed to ~2x display size, white backgrounds removed — see design/brand/build/).
import { readFileSync, writeFileSync } from "node:fs";

const tpl = readFileSync("index.template.html", "utf8");
const tokens = readFileSync("design/tokens.css", "utf8");
const data = JSON.parse(readFileSync("data/pilot50.json", "utf8")).recipients;
const b64 = f => "data:image/png;base64," + readFileSync(`design/brand/build/${f}`).toString("base64");
const assets = {
  star: b64("star-64.png"),
  medalArmy: b64("medal-army-208.png"),
  medalNavy: b64("medal-navy-208.png"),
  medalAF: b64("medal-af-208.png"),
};

// replacer functions throughout so "$"-sequences in citations/base64 are never treated as patterns
let out = tpl
  .replace("/*__TOKENS__*/", () => tokens)
  .replace("const PILOT = /*__DATA__*/[];", () => "const PILOT = " + JSON.stringify(data) + ";")
  .replace("const ASSETS = /*__ASSETS__*/{};", () => "const ASSETS = " + JSON.stringify(assets) + ";");

for (const ph of ["__TOKENS__", "__DATA__", "__ASSETS__"]) {
  if (out.includes(ph)) throw new Error(`placeholder ${ph} not replaced`);
}
if (data.length !== 50) throw new Error(`expected 50 records, got ${data.length}`);
writeFileSync("index.html", out);
console.log(`index.html written: ${out.length} bytes, ${data.length} records, assets ${Object.keys(assets).join("/")}`);
