# CLAUDE.md — Medal of Honor Stories Browser

You are the dedicated agent for the MOH Stories Browser: a single-file HTML app for
browsing and filtering Medal of Honor recipient stories. Built for Darrin (project
originator) to discover stories by theme. You run unattended — work through the task
queue in order, commit as you go, and leave a session log entry in NOTES.md each run.

## Mission
A fast, beautiful, mobile-first browser of MOH stories filterable by: 32 thematic
categories (4 groups), branch, war/conflict, battle, survived/fallen, plus text
search — with a card grid, detail view with full citation, saved views, and a map.
The official cmohs.org site's filtering is poor; combinable filters are our edge.

## Current state (as of handoff, 2026-07-30)
- data/pilot50.json — 50 curated recipients, app-ready schema, DONE. Fields: id,
  name, rank, branch, unit, conflict, battle, year, action_date, action_place,
  coords{lat,lng}, survived, accredited_to, born, citation, category_hints,
  categories[] (EMPTY — Phase 2 fills these), photo_url (null), cmohs_link.
- data/medal_of_honor.json — full CORGIS source dataset, 3,475 records (public
  domain US gov citations + geocoded locations). Phase 5 source. Known gaps: no
  conflict field, no posthumous flag, no photos, ends ~2014 presentations.
- quitters-reuse-spec.md — the Phase 3 build spec: architecture, design tokens,
  filter engine code, feedback system, lessons learned. FOLLOW IT.
- NOTES.md — running project log. Append, never rewrite history.

## Task queue (work in order)
1. PHASE 2 — Category tagging. Read each pilot50 citation + category_hints and
   assign 1-4 categories from the 32 below. Write into categories[]. Also verify
   the survived flag against citation language; flag disagreements in NOTES.md
   rather than silently changing hand-assigned values. Idempotent: never re-tag a
   record that already has categories unless asked. A calibration set of 59
   hand-tagged stories from Darrin may arrive later — when it does, diff against
   it and tune.
2. PHASE 3 — Build the app: ONE self-contained index.html. Embed pilot50.json
   inline. Implement per quitters-reuse-spec.md: multi-select filter menus with
   live per-option faceted counts (compute each dimension's counts with that
   dimension's own filter removed), active-filter chips, clear-all, 180ms
   debounced search with match highlighting, saved views (localStorage is fine
   here — this is a real browser, not an artifact), card grid, detail modal with
   full citation + history.pushState back-button support, light/dark/auto theme,
   print styles, toast feedback. 4 accent colors = the 4 category groups (thin
   bars/chips only, never fills). Mobile-first. Escape ALL data at render
   (citations contain quotes/apostrophes/ampersands).
3. PHASE 4 — Map view: pins from coords (Leaflet via CDN is acceptable), popup =
   name + place + link to detail. Note pins are approximate.
4. PHASE 5 — Scale: transform all 3,475 records (derive conflict from year +
   location + citation text; infer survived; tag categories in batches;
   fingerprint inputs so re-runs skip unchanged records). Test performance with
   lazy rendering (chunked, ~200 cards per rAF) BEFORE shipping full set.
5. PHOTOS (opportunistic) — Wikimedia/Wikipedia portraits (mostly public domain
   military photos). Store URL + attribution per record. Never hotlink cmohs.org
   images without their page credit; their portrait photos can be third-party
   copyrighted.
6. TOP-UP (later) — post-2014 recipients (2021-22 Vietnam upgrades: Birdwell,
   Kaneshiro, Duffy, Fujii; recent GWOT and Korea/Vietnam reviews) from Wikipedia.

## The 32 categories (Darrin's taxonomy — do not rename)
The Deed (what earned it): 1 The Assault · 2 The Last Stand · 3 The Body on the
Grenade · 4 The Rescue & Lifesaver · 5 The Healer Under Fire · 6 The Colors ·
7 One Against Many · 8 The Raid · 9 Wings · 10 The Sea · 11 Unbroken in Captivity ·
12 The Rallying Point
The Person (who they were): 13 The Reluctant Warrior · 14 The New American /
Immigrant's Debt · 15 The Trailblazer / The First · 16 The Boy (Too Young for
This) · 17 The Career Warrior · 18 The Citizen-Soldier · 19 The Twice-Honored
The Spirit (why it moves us): 20 Religious / Faith-Driven · 21 Miraculous / Left
for Dead · 22 Greater Love · 23 Redemption / The Second Birth · 24 Brotherhood /
No One Left Behind · 25 Duty & Country (Patriotic) · 26 The Cost of War / Lament
The Aftermath (life beyond the medal): 27 The Fallen / Ultimate Sacrifice ·
28 The Quiet Return · 29 Belated Justice / The Long Vindication · 30 The Forgotten
Hero / Fall From Grace · 31 The Wounded Warrior · 32 The Epic Second Act
Multiple categories per story allowed; 1-4 is the sweet spot. Deed categories come
from the citation; Person/Spirit/Aftermath may need the hints or brief research.

## Hard rules
- Single-file discipline governs the SHIPPED ARTIFACT, not the repo. The shipped
  product (index.html) is one self-contained file, zero build step, zero external
  deps except Leaflet CDN for the map. But the repo is template-as-source (see
  Architecture below): index.template.html is the source of truth and is REQUIRED —
  never delete it. index.html is a build artifact, rebuilt from the template via the
  inject step and always committed alongside it so the shipped file stays standalone.
  All colors via CSS custom properties; grep for raw hex outside the token block
  before every commit (spec §1).
- One agent session at a time. Only a single agent session may operate on this repo
  concurrently. Do NOT run parallel sessions — concurrent writers cause template-vs-
  index churn and conflicting pushes. If you observe another session's commits under a
  different identity, stop and log it rather than racing.
- Escape everything rendered from data (rpEsc pattern in spec §5).
- Never overwrite human-provided values (category_hints, Darrin's calibration
  tags, hand-assigned conflict/survived) — log disagreements instead.
- Citations are public domain; render them in full, verbatim. Do not editorialize
  or summarize citations inside the app.
- Respect the subject matter: no gamification language, no dark-pattern UI. This
  may be shown to veterans' families and used by teachers — print styles matter.
- git init if not a repo; small commits with clear messages; never force-push.
- End every session by appending a dated summary to NOTES.md (what changed, what's
  next, any open questions for the humans).

## Architecture — template-as-source (human ruling, 2026-07-30)
Permanent, settled architecture. Do not re-litigate.
- index.template.html is the SOURCE OF TRUTH. It carries the page chrome/markup plus
  two inject placeholders: `/*__TOKENS__*/` (inside `<style id="tokens">`) and the
  data slot `const STORIES = /*__DATA__*/[];`.
- index.html is a BUILD ARTIFACT. Rebuild it from the template by the inject step,
  then commit it alongside the template in the same session. Never hand-edit index.html
  as the primary source — edit the template (or the tokens/data inputs) and rebuild.
- Inject step (no build script; done inline/reproducibly): replace `/*__TOKENS__*/`
  with the tokens CSS (design/tokens.css + the --tg-person violet amendment) and
  replace the literal `const STORIES = /*__DATA__*/[];` with
  `const STORIES = <pilot data array>;`. Nothing else changes.
- Every rebuild must re-validate: correct record count, valid JSON, category_hints
  intact, `node --check` clean, zero raw hex outside the tokens block. Confirm the
  template and index.html are in sync before pushing.

## GitHub workflow
Canonical repo: EMW81/moh-app (https://github.com/EMW81/moh-app.git) — permanent
origin. PRODUCTION: main is auto-deployed to https://everymedal.org via GitHub Pages —
every push is a live production deploy. Never push a broken index.html; verify the
build renders (record count, node --check, visual smoke test) before every push.
Standing procedure every session:
- START: `git pull --rebase origin main` before doing any work, to take remote
  changes cleanly.
- DURING: small, focused commits as you go (never batch a session into one commit).
- END: `git push origin main` — include the NOTES.md session-log commit in the push.
- AUTH FAILURE: if pull/push fails on authentication, STOP and log it in NOTES.md.
  Never touch, prompt for, or modify git credentials.
- Never force-push and never rewrite published history (no rebase/amend of pushed
  commits, no `push --force`).
