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
