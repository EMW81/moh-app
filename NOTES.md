# MOH Stories App — Build Notes

## Session 2026-07-30 (eve) — Phases 2 & 3 shipped
CHANGED:
- PHASE 2 (category tagging) COMPLETE. All 50 pilot recipients now carry 1-4 of
  the 32 canonical themes in `categories[]`. Tagged by reading each full citation +
  category_hints, calibrated against the 6 pre-tagged stories in
  design/stories.sample.json. Every assignment validated against the canonical
  32-name set; 1-4 per record (Shughart trimmed 5->4 for the sweet spot).
  Survived flags: verified all 50 against citation language — NO disagreements,
  so no human-assigned values were changed. Live group story-counts:
  Deed 50 · Person 18 · Spirit 21 · Aftermath 34. Fate: 33 survived / 17 fell.
  (Note: the README's rail placeholder counts 61/21/28/37 were designer mock
  numbers; the app now computes real faceted counts live.)
- PHASE 3 (app) COMPLETE. Single self-contained index.html (~160KB, zero build
  step, zero deps). Implements the Meridian "Stories of Valor" design from
  design/README.md. Built from index.template.html via an inline inject step
  (tokens + data), kept in-repo for reproducible rebuilds.
- Design handoff unpacked into design/ (README.md, tokens.css, stories.sample.json,
  DESIGN_BRIEF.md) from the "MoH Stories Browser mockup.zip" in ~/Downloads.

DESIGN AMENDMENTS APPLIED (per Darrin/handoff instructions):
  1. --tg-person remapped to violet (#7c3aed light / #a78bfa dark). Gold (#a16207)
     is now reserved exclusively for the fallen — person no longer collided with it.
  2. Header avatar omitted (theme toggle sits top-right instead).
  3. README's React/Vue line ignored — single-file vanilla per CLAUDE.md.
  4. URL-encoded filter state adopted (shareable ?q/t/c/b/f/s params; back button
     closes the detail modal via history.pushState).

BUILT (browse view matches mockups 2A/2B, light + dark, verified via headless
Chrome screenshots): 230px theme-responsive rail (wordmark, nav w/ live badges,
theme-group color bars w/ live counts, footer note); header; filter row (search +
Themes/Conflict/Branch popovers + All/Survived/Fell segment); count bar; 3-col
card grid (avatar initials, 4-block dept-seg group indicator, mono meta line,
3-line excerpt, lead theme chip +N, fate chip). Plus: theme menu popover (4
columns, live faceted counts computed with each dimension's own filter removed),
active-filter chips + clear-all, saved views (localStorage), 180ms debounced
search with match highlighting on cards + detail, story detail modal (two-column,
full verbatim citation — stress-tested with the 4,587-char Benavidez citation),
light/dark/auto theme (persisted), print styles, toast, empty state. All colors
via CSS custom properties (grep confirms zero raw hex outside the token block);
tokens.css embedded verbatim + the person-color amendment. Everything rendered
from data is escaped (esc()).

NEXT:
- PHASE 4 — Map view (Leaflet + CARTO tiles; coords already present). Header
  List/Map toggle is speced but not yet wired — deferred to keep this session's
  gate ("push when the browse view renders") clean.
- Battle facet: state/data support it but the filter row shows only the 3 speced
  dropdowns (Themes/Conflict/Branch) to match 2A/2B. Add a Battle menu later.
- Calibration: when Darrin's 59 hand-tagged stories arrive, diff against my Phase 2
  tags and tune (esp. Person/Spirit judgment calls).

OPEN QUESTIONS FOR HUMANS:
- Remote/push: no git remote was configured. Need the target repo (and whether it
  should be public or private) before pushing.

## Status (2026-07-30, PM)
- Phase 1 (data pull) COMPLETE for pilot: 50 curated recipients in data/pilot50.json.
  SOURCE PIVOT: cmohs.org bot-blocked mid-scrape. Switched to the CORGIS public
  medal_of_honor dataset (github: corgis-edu/corgis) — 3,475 records, full citations,
  GEOCODED action locations (lat/lng! map = nearly free), saved at data/medal_of_honor.json.
  Known dataset gaps: no conflict field (hand-assigned for pilot; AI-derive at scale),
  no posthumous flag (hand-assigned for pilot; AI-verify at scale), no photos,
  ends ~2007 actions / ~2014 presentations (post-2014 awards need a top-up scrape later,
  e.g. from Wikipedia: 2021-22 Vietnam upgrades, Birdwell, Kaneshiro, recent GWOT).
- Phase 2 (category tagging): ready to run on pilot50. Want Darrin's 59 hand-tagged
  stories to calibrate. category_hints field pre-seeded per recipient.
- Phase 3 (app): spec = quitters-reuse-for-moh-browser.md (project file). Pilot data
  embeds inline in the single HTML artifact (114KB). Photos deferred (see below).
- PHOTOS: open question. cmohs.org blocks server-side fetches; options: (a) ship pilot
  without photos, (b) Wikipedia/Wikimedia portraits (mostly public domain military
  photos) added per-record later, (c) user-side hotlinking if we can recover media URLs.
- Quitters components adopted: filter engine w/ multi-select + chips + saved views,
  faceted counts (per-option, own-dim-removed), toast feedback, tokens-only theming
  (4 category-group accents), debounced search + highlight, print styles, mobile-first.

## Site recon findings (cmohs.org)
- 3,536 total recipients, 297 listing pages x 12 per page.
- Profile URL pattern: /recipients/{slug}. Each profile has:
  - Details: Rank, Conflict/Era, Unit/Command, Branch, Action Date, Action Place
  - Full official citation text (US gov work, public domain)
  - Photo (meta-image tag). NOTE: portrait photos may be third-party copyrighted
    (e.g. "copyright Nick DelCalzo") — hotlink + credit, don't redistribute.
  - Additional: Accredited to, Awarded Posthumously (Y/N — our survival filter),
    Presentation date, Born, Died, Buried. Some have video (Vimeo) + photo gallery.
- Listing filters via query params: ?conflicts[]=slug, ?branches[]=slug (26 conflicts, 13 branches).
- ~35 curated lists at /recipients/lists/{slug}: battles (Iwo Jima=27, Gettysburg,
  Chosin, Tet, D-Day...), plus Living, Double Recipients, Chaplains, Medics/Corpsmen,
  Submariners. These power the "battle" filter for free.

## Scraping approach
- All fetches via web_fetch (container network is locked to package registries).
- Batch profile pulls ~8-10 per message to keep turns manageable.
- Pilot-50 diversity targets: every conflict era represented, all major branches,
  mix of survived/posthumous, at least one each of: POW, chaplain, medic, aviator,
  sea story, living recipient, double recipient if possible, Mary Walker (only woman).

## Data model (see data/recipients.json)
One JSON record per recipient; categories[] filled in Phase 2; coords geocoded Phase 4.

## Darrin's 32 categories
The Deed: Assault, Last Stand, Body on the Grenade, Rescue & Lifesaver, Healer Under
Fire, The Colors, One Against Many, The Raid, Wings, The Sea, Unbroken in Captivity,
Rallying Point.
The Person: Reluctant Warrior, New American/Immigrant's Debt, Trailblazer/The First,
The Boy, Career Warrior, Citizen-Soldier, Twice-Honored.
The Spirit: Religious/Faith-Driven, Miraculous/Left for Dead, Greater Love,
Redemption/Second Birth, Brotherhood/No One Left Behind, Duty & Country, Cost of War/Lament.
The Aftermath: The Fallen, Quiet Return, Belated Justice, Forgotten Hero/Fall From
Grace, Wounded Warrior, Epic Second Act.
Multiple categories per story allowed.

## Session 2026-07-30 (PM 2) — Phase 3 build shipped

CHANGED
- Phase 2 confirmed COMPLETE: all 50 pilot recipients already carry categories[]
  (1–4 each, 29 distinct themes in use, all mapping cleanly to the 4 groups). No
  re-tagging done (idempotent rule); survived flags left as hand-assigned.
- Design handoff read (design/README.md + tokens.css + mockup canvas). Chosen
  direction: Meridian, options 2A (light) / 2B (dark).
- tokens.css AMENDED per instruction: --tg-person → violet (#7c3aed light /
  #a78bfa dark); gold now reserved exclusively for the fallen. Otherwise verbatim,
  embedded inline in index.html.
- Built index.html — ONE self-contained file, zero build step, deps only Leaflet CDN
  (map) + Geist/Geist Mono. pilot50 embedded inline. Implements: 230px theme-
  responsive rail (Stories/Map/Saved views + live faceted group counts), header with
  NO avatar (amendment), 180ms debounced search + match highlight, Themes 4-col
  popover + Conflict/Branch dropdowns with per-option faceted counts (own-dim-removed),
  fate segmented, active-filter chips + clear-all, saved views (localStorage), 3-col
  card grid (dept-seg 4-block indicator, lead theme chip + "+N", fate chip), count bar,
  empty state, detail modal (citation verbatim & in full, history.pushState back-button,
  deep-linkable), Leaflet map (CARTO light/dark tiles, accent-dot=survived /
  gold-star=fell, popups → detail), light/dark/auto theme (persisted, OS-following),
  print styles, toasts.
- URL-ENCODED filter+search+view+story state (amendment #4): shareable + back-button
  (compact index-based ?t/c/b, plus ?q/?f/?v/?s).
- All rendered data escaped (esc()). Token discipline verified: 0 raw hex in app CSS.

VALIDATED (headless Chrome, zero app-level JS errors): browse light (matches 2A),
browse dark (matches 2B), map view, deep-linked detail modal.

DEVIATIONS / NOTES
- An index.template.html scaffold (same tokens/placeholder scheme, Meridian classes,
  SVG icons) was present when the build started — a strong near-complete Phase 3
  implementation. Adopted it, added the missing Map view + reconciled nav/popstate,
  then inlined tokens+data and REMOVED the template to keep single-file discipline
  (index.html stands alone; edit it directly henceforth).
- Battle NOT surfaced as a 4th dropdown (2A shows only Themes/Conflict/Branch — matched
  the hifi exactly). Battle data is present; easy to add later.
- Print currently prints the open detail (chrome hidden) rather than the bespoke 1H
  sheet; acceptable for pilot, refine later.

NEXT / OPEN QUESTIONS
- git remote: none configured — committed locally; needs a remote before I can push.
- Phase 4 (map) effectively done for the pilot. Phase 5 = scale to 3,475.
- Awaiting Darrin's 59-story calibration set to tune Phase 2 tags.
- Photos deferred (Wikimedia); card avatar swaps to photo_url when present.

## Session 2026-07-30 (eve 2) — Phase 4 map, Battle facet, Phase 5 prep

CHANGED (all committed + pushed to origin EMW81/moh-app):
- Reviewed the uncommitted index.html working change: it re-embedded the human
  category_hints into the inline data (good — restores pilot50.json fidelity) but
  had introduced a stray `[]` after the STORIES array literal (`= [...][];`), a JS
  syntax error that blanked the app. Kept the hints, removed the bracket (ce2768b).
- CLAUDE.md: added a "GitHub workflow" section — canonical origin EMW81/moh-app,
  pull --rebase at start, small commits, push (with NOTES) at end, stop+log on auth
  failure without touching creds, never force-push/rewrite history (fc0df79).
- PHASE 4 (map) wired + built: Leaflet 1.9.4 + CARTO light/dark tiles that follow
  the theme, faceted pins (survived dot / fallen star), popup -> detail, List/Map
  rail toggle with ?v=map URL state, approximate-location disclaimer, graceful
  degradation if Leaflet fails. Verified in headless Chrome (e14771f).
- BATTLE facet added as a 4th filter menu (Themes/Conflict/Branch/Battle): 27
  distinct battles, per-option faceted counts, chips, ?bt= URL state, saved-view
  support. Verified filtering to Iwo Jima (9b5190d).
- PHASE 5 PREP: renderGrid now chunks ~200 cards/frame via rAF with a cancel token,
  so the full ~3,475 set won't block paint. No-op for the 50-record pilot (843d029).

BUILD MODEL USED THIS SESSION: index.template.html = source of truth (has the
/*__TOKENS__*/ and /*__DATA__*/ placeholders); index.html rebuilt from it by
injecting tokens (from HEAD) + pilot50 data. Every rebuild re-validated: 50 records,
valid JSON, category_hints intact, node --check clean, zero raw hex outside tokens.

OPEN QUESTION / CONFLICT FOR HUMANS (important):
- A concurrent writer (commits authored as ericwilsonart@gmail.com, a different
  identity than this session's claimtheacre@gmail.com) is operating on this repo in
  parallel. Its own NOTES entry ("Session 2026-07-30 PM 2") states it REMOVED
  index.template.html "to keep single-file discipline" and wants index.html edited
  directly. This session (and the "eve" session) instead KEEP the template as the
  source of truth for reproducible rebuilds. During this session the template was
  repeatedly deleted from the working tree and my uncommitted edits reverted by that
  process; I restored the template and committed. NET: both approaches' work is on
  origin, but they are architecturally at odds. Humans must decide: (a) template-as-
  source (keep index.template.html, build index.html from it), or (b) single-file only
  (delete the template, edit index.html directly). Until settled, expect churn.
  No history was rewritten and nothing was force-pushed.

## Session 2026-07-30 (eve 3) — Human ruling: template conflict RESOLVED

RULING RECEIVED (from the humans) and APPLIED:
- (a) TEMPLATE-AS-SOURCE is the permanent architecture. index.template.html is the
  source of truth; index.html is a build artifact, rebuilt via the inject step and
  always committed alongside so the shipped product stays a zero-build single file.
  The template is REQUIRED — never delete it. This is settled; do not re-litigate.

CHANGED:
- CLAUDE.md: amended the single-file hard rule to state that single-file discipline
  governs the SHIPPED ARTIFACT (index.html), not the repo; the template is required.
  Added an operational hard rule: ONE agent session at a time (no parallel writers).
  Added a new "Architecture — template-as-source" section documenting the inject
  placeholders (/*__TOKENS__*/, const STORIES = /*__DATA__*/[];), the inject step,
  and the per-rebuild validation checklist.
- Git identity: set this repo's local config to user.email ericwilsonart@gmail.com,
  user.name EMW81, so future commits from this repo are consistent.

VERIFIED (no restore/rebuild needed):
- index.template.html is present on origin/main (the concurrent session's deletion
  did NOT reach origin — nothing to restore). Working tree clean, in sync with origin.
- Template ↔ index.html SYNC confirmed: re-running the inject step (tokens + data
  extracted from index.html, injected into the template) reproduces index.html
  byte-for-byte. Data re-validated: 50 records, valid JSON, all 50 carry
  category_hints and 1–4 categories[].

NEXT:
- Resume the task queue: Phase 5 (scale to 3,475) is the next substantive work.
- Calibration: still awaiting Darrin's 59 hand-tagged stories to tune Phase 2.
- Going forward: edit the template + inputs and rebuild index.html; never hand-edit
  index.html as source. Run only one session at a time.

---

## 2026-07-30 — Card-width control (3/2/1-across + reading-list mode)

Feature request (human): add a segmented control at the right end of the filter
toolbar to set the grid's max column count, with a distinct 1-across reading-list
mode. Persist in localStorage + URL.

CHANGED (template-as-source: edited index.template.html, then rebuilt index.html):
- Toolbar: new `.seg.cols-seg` (right-aligned via margin-left:auto) with 3/2/1
  buttons, tooltips + aria-labels. Mono tabular digits.
- Grid CSS: driven by `data-cols` on #grid.
  - data-cols="2" → 2 columns; data-cols="1" → reading list:
    single column `minmax(0,75ch)`, centered (`justify-content:center`), and
    excerpt line-clamp bumped 3→9.
  - The chosen value is a MAX. Responsive cap unchanged in spirit: ≤1080px caps
    3→2 (`:not([data-cols="1"]):not([data-cols="2"])`); ≤820px forces single
    column for every choice (attribute-specificity match so it overrides the
    75ch cap and fills narrow screens).
- JS: `state.cols` (default 3); `loadCols()` reads `moh_cols` from localStorage;
  `?cols=` URL param (written when ≠3, read with URL-wins-over-localStorage
  precedence). `setCols()` persists + re-renders. cardHTML widens the excerpt to
  ~3x (170→540 snippet / 190→570 plain) when cols===1. render()/popstate set
  `#grid[data-cols]` and call `syncColsUI()`.
- Bugfix guard: the fate seg and cols seg both use `.seg-btn`; retargeted the
  fate click handler and `syncFateUI()` from `.seg-btn` to `[data-fate]` so the
  two segmented controls don't clobber each other's active state.

VERIFIED:
- Rebuild validation: 50 records, valid JSON, all 50 category_hints intact,
  `node --check` clean, zero raw hex outside the tokens block, template ↔ index.html
  in sync (22 feature markers each).
- Headless-Chrome screenshots, all three widths in BOTH light and dark: 3-across
  and 2-across grids render correctly; 1-across is a centered ~75ch reading list
  with the long excerpt; active button state correct in each. Responsive check at
  900px: cols=3 correctly collapses to 2.

NEXT:
- Unchanged: Phase 5 (scale to 3,475) is the next substantive work; still awaiting
  Darrin's 59-story calibration set.

---

## 2026-07-30 (eve, session: modal-z-index bugfix)

BUG: From Map view, clicking "Read the story" in a Leaflet pin popup opened the
detail modal BEHIND the map — partially hidden, unreadable, uncloseable.

ROOT CAUSE: `.detail-scrim` had `z-index:60`. It is (correctly) a direct child of
`<body>`, but `.mapwrap`/`main`/`.app` create NO stacking context (no positioned
ancestor with a z-index), so Leaflet's panes/controls (z-index ~700–1000) lived in
the same root stacking context and painted over the modal.

FIX (template-as-source; edited template + tokens.css, rebuilt index.html):
- New token `--z-modal:2000;` in design/tokens.css `:root` (geometry section) —
  flows into the `<style id="tokens">` block on rebuild. 2000 > Leaflet's ~1000.
- `.detail-scrim` z-index `60` → `var(--z-modal)`. position:fixed + z-index makes
  its own stacking context above everything Leaflet; inset:0 + backdrop + default
  pointer-events intercept clicks/scroll so pan/zoom can't be reached; body
  overflow already pinned hidden while open.
- `openDetail()` now calls `if(MAP) MAP.closePopup();` so the pin popup dismisses
  as the modal takes over.

VERIFIED (headless Chrome via puppeteer-core driving the REAL app + Leaflet CDN):
- 69/69 automated checks. Map view, actual pin→popup→"Read the story" flow, in
  light AND dark × cols 3/2/1: modal open, scrim covers viewport, element at
  viewport centre resolves INTO #detailScrim (was a leaflet layer before),
  computed z-index=2000, popup closed on open, and all three close paths (X,
  backdrop, Escape) work. List-view spot check: card→modal still opens topmost and
  closes on Escape — unchanged path.
- Rebuild validation: 50 records, valid JSON, 50/50 category_hints intact,
  `node --check` clean, zero raw hex outside tokens, index.html diff = only the 3
  intended changes.

NEXT:
- Same as before: Phase 5 scale-up + awaiting Darrin's 59-story calibration set.
- Incoming (this queue): 1-across centering nudge, Photos phase (50 pilot), and
  photo-on-card design — starting now.

---

## 2026-07-31 (session: photos phase + photo-card design)

LAYOUT (1-across centering): investigated the reported "card column offset to the
right." Measured in headless Chrome at 3 widths: card centre === toolbar centre ===
countbar centre (835px, 0px offset) — already dead-centred within the content area.
The rightward *feel* is the 230px sidebar shifting the whole content area right.
Asked the human; ruling = keep content-area centering (aligned with the toolbar).
NO code change. Not a bug.

PHOTOS (pilot 50) — 48/50 found (96%). Method: MediaWiki API only (no scraping,
no hallucinated URLs) — generator=search "<name> Medal of Honor" → pageimages
`original` → derive File: from the upload.wikimedia URL → imageinfo `extmetadata`
for license + a 500px `thumburl`. Accept PD or permissive CC; every accepted URL
was HTTP-verified to return image/* (200). Article matching was correct for all 50.
- License mix: 47 public domain, 1 CC BY 2.0 (John Basilone — credit "USMC Archives
  from Quantico, USA / Wikimedia Commons — CC BY 2.0").
- MISSES (2, left null): `charles-windolph` (no image on any Commons file);
  `freddie-stowers` (killed 1918 — Commons has only his grave & the posthumous
  ceremony, no portrait). Skipped per "no clearly-licensed portrait" rule.
- CORRECTION: `fred-w-stockham` — Wikipedia's top hit was "USNS GySgt. Fred W.
  Stockham" (a SHIP named for him); its lead image was the vessel. Replaced with the
  real USMC portrait File:Fred W. Stockham - WWI Medal of Honor Recipient.jpg (PD).
- Also rejected two grave/ship lead-images caught by a non-portrait filename scan;
  false-positives (Whittlesey, Adkins — "Medal_of_Honor" in filename) kept.
- pilot50.json: added `photo_credit` (new field, placed after photo_url) + populated
  `photo_url`. Only photo fields changed; category_hints/categories untouched.

CARD DESIGN:
- 1/2-across: portrait is a full-card-height strip on the LEFT edge (122px, object-fit
  cover, clipped to the card's 8px radius via card overflow:hidden, `border-right`
  token divider). Card flips to `flex-direction:row`; content wrapped in `.card-main`.
  The small round avatar is hidden in these modes (strip replaces it).
- 3-across: unchanged compact layout; the round `.avatar` swaps to the photo `<img>`
  when present (the avatar already supported `img` + overflow:hidden).
- No-photo cards: 3-across keeps initials avatar; 1/2-across shows a quiet `.ph`
  placeholder (initials on `--surface-raised`, no broken-image icon).
- All images `loading=lazy decoding=async`.
- Detail modal: portrait at top of the meta rail (`.detail-portrait`, 4:5, capped
  150px) + credit line under the rail (`.meta-credit`); both omitted when no photo.
  No credit on cards, per spec.

VERIFIED (headless Chrome, real Wikimedia images over network):
- 1/2/3-across in BOTH light and dark, with-photo (jacob-parrott) and no-photo
  (charles-windolph): strip visible+img in 1/2 (122px, full height) with avatar
  hidden; avatar+img in 3 with strip hidden; initials placeholder for no-photo;
  images actually loaded (naturalWidth 500). Modal: portrait + PD credit shown for
  a photo record, both absent for a no-photo record. Screenshots eyeballed.
- Rebuild: 50 records, 48 photos, `node --check` clean, zero raw hex outside tokens,
  template ↔ index.html photo-feature markers in sync (11 each).

NEXT:
- Phase 5 scale-up (3,475) — at scale, run the same MediaWiki-API photo pass in
  batches with input fingerprinting. Still awaiting Darrin's 59-story calibration set.
