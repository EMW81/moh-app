# MOH Stories App — Build Notes

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
