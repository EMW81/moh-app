#!/usr/bin/env node
// Phase-5 MERGE: data/pilot50.json + data/tagged/chunk_01..14.json -> data/stories.json
// Order: the 50 curated pilot records FIRST (they are the inline instant-render set, so
// the top of the list doesn't reshuffle when the full set swaps in), then tagged chunks
// in chunk order. Pilot records are authoritative — the pre-pass already excluded their
// cmohs numbers from the chunks; this script re-verifies that invariant.
import { readFileSync, writeFileSync } from "node:fs";

const pilot = JSON.parse(readFileSync("data/pilot50.json", "utf8")).recipients;
const cmohsNum = link => (String(link || "").match(/recipient-detail\/(\d+)\//) || [])[1] || null;

const all = [...pilot];
for (let i = 1; i <= 14; i++) {
  const n = String(i).padStart(2, "0");
  const chunk = JSON.parse(readFileSync(`data/tagged/chunk_${n}.json`, "utf8"));
  if (chunk.count !== chunk.records.length) throw new Error(`chunk ${n}: count mismatch`);
  all.push(...chunk.records);
}

// Year-truncation repairs — 3 CORGIS source records carry truncated years, which also
// mis-derived one conflict. Derived-field corrections only (citation text is the
// evidence); human-assigned values are never touched. Logged in NOTES 2026-07-31.
const REPAIRS = {
  "robert-b-nett":  { year: 1944, action_date: "1944-12-14", conflict: "World War II", conflict_uncertain: false,
                      conflict_reason: "year repaired 194->1944 (citation: Leyte, Philippine Islands, 14 December 1944)" },
  "george-c-platt": { year: 1863, action_date: "1863-7-3", conflict: "U.S. Civil War", conflict_uncertain: false,
                      conflict_reason: "year repaired 63->1863 (Fairfield PA flag action, 3 July 1863)" },
  "david-goodman":  { year: null, action_date: null, conflict: "Indian Campaigns", conflict_uncertain: true,
                      conflict_reason: "source year truncated (186X, digit unrecoverable); 8th US Cavalry, Arizona -> Indian Campaigns" },
};
for (const r of all) if (REPAIRS[r.id]) Object.assign(r, REPAIRS[r.id]);

// Category-name normalization: the tagging prompt's long-form label for #25 -> the
// app's display label (same category, Darrin's taxonomy unchanged).
const CAT_ALIASES = { "Duty & Country (Patriotic)": "Duty & Country" };
for (const r of all) r.categories = r.categories.map(c => CAT_ALIASES[c] || c);

// validations
const ids = new Set(), nums = new Set();
const pilotNums = new Set(pilot.map(r => cmohsNum(r.cmohs_link)).filter(Boolean));
let fell = 0, noPhoto = 0, uncertain = 0;
for (const r of all) {
  if (ids.has(r.id)) throw new Error(`duplicate id: ${r.id}`);
  ids.add(r.id);
  const num = r.cmohs_num || cmohsNum(r.cmohs_link);
  if (num) {
    if (nums.has(num)) throw new Error(`duplicate cmohs num: ${num} (${r.id})`);
    nums.add(num);
  }
  if (r.cmohs_num && pilotNums.has(r.cmohs_num)) throw new Error(`tagged record overlaps pilot: ${r.id}`);
  if (!Array.isArray(r.categories)) throw new Error(`categories not array: ${r.id}`);
  if (typeof r.survived !== "boolean") throw new Error(`survived not boolean: ${r.id}`);
  if (typeof r.conflict !== "string" || !r.conflict) throw new Error(`bad conflict: ${r.id}`);
  if (typeof r.citation !== "string" || !r.citation) throw new Error(`bad citation: ${r.id}`);
  if (!r.survived) fell++;
  if (!r.photo_url) noPhoto++;
  if (r.conflict_uncertain) uncertain++;
}
if (all.length !== 3475) throw new Error(`expected 3475 records, got ${all.length}`);

const out = JSON.stringify(all);
writeFileSync("data/stories.json", out);
console.log(`data/stories.json: ${all.length} records, ${out.length} bytes`);
console.log(`fell=${fell} noPhoto=${noPhoto} conflict_uncertain=${uncertain}`);
