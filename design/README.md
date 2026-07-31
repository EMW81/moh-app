# Handoff: Stories of Valor — Medal of Honor Stories Browser (Meridian)

## Overview
A browser for Medal of Honor citations ("Stories of Valor"): 50-story pilot (of 3,536), searchable and filterable by a 32-theme taxonomy organized into 4 groups, plus conflict / branch / battle / fate facets, with list + map views, a citation-verbatim detail view, saved views, and a print sheet. The chosen visual direction is **Meridian** — the design system from the QUITTERS Art Dept HQ app (light-first zinc neutrals, one indigo accent, 6–8px radii, soft shadows, tinted pill chips, Geist / Geist Mono, theme-responsive left rail, full dark mode).

## About the Design Files
The files referenced here are **design references created in HTML** — prototypes showing intended look and behavior, not production code to copy directly. The task is to **recreate these designs in the target codebase's existing environment** (React, Vue, etc.) using its established patterns — or, if no environment exists yet, choose the most appropriate framework and implement there. If the target codebase is the QUITTERS/Meridian codebase itself, reuse its existing classes and tokens (`.btn`, `.chip-*`, `.dept-chip`, `.dept-seg`, `.card`, rail/nav patterns) rather than re-implementing them.

## Fidelity
- **High-fidelity**: the Browse view, desktop 1280, light AND dark (options 2A/2B in the mockup file). Recreate pixel-perfectly.
- **Specified, to derive in Meridian**: Theme menu, active-filter state + saved views, Story detail, Map view, Empty state, Mobile (390), Print sheet. These exist as hifi mockups in a sibling visual language (options 1B–1N); their **structure, content, and behavior are final** — restyle them with the Meridian tokens and component recipes below. Where this README specifies a Meridian treatment, it wins over the 1x mockups' styling.

## Design Tokens (paste-ready)
See `tokens.css` in this folder — verbatim from the Meridian source (`QUITTERS_Art_Dept_HQ_9.html` §tokens) plus this product's four theme-group colors mapped onto Meridian's dept ramp.

Key values:

**Light (default)**
- bg `#fafafa` · surface `#ffffff` · surface-raised `#f4f4f5`
- border `#e4e4e7` · border-strong `#d4d4d8`
- text `#18181b` · text-muted `#52525b` · text-subtle `#a1a1aa`
- accent `#5b5bd6` (hover `#4f4fc8`, pressed `#4646b8`, tint bg `#eeeef8`, fg `#ffffff`)
- gold (fallen) `#a16207` · neutral `#71717a` · warning `#b45309`
- theme groups: deed `#c2410c` · person `#a16207` · spirit `#15803d` · aftermath `#0369a1`
- shadows: sm `0 1px 2px rgba(0,0,0,.05)`; md `0 1px 3px rgba(0,0,0,.07), 0 4px 14px rgba(0,0,0,.05)`
- focus ring `0 0 0 3px rgba(91,91,214,.28)`

**Dark (`[data-theme="dark"]`)**
- bg `#0f0f11` · surface `#161618` · surface-raised `#1f1f23`
- border `#26262b` · border-strong `#313138`
- text `#ededf0` · text-muted `#9d9da6` · text-subtle `#66666e`
- accent `#7b83eb` (solid `#5e5edd`, tint `rgba(123,131,235,.14)`)
- gold `#d9b13b` · neutral `#8f8f98` · warning `#e5a13c`
- theme groups: deed `#fb923c` · person `#eab308` · spirit `#4ade80` · aftermath `#4db8f0`
- rail: bg `#131316` · raised `#232329` · border `#202024` (rail is theme-responsive: light rail chains to light neutrals)
- focus ring `0 0 0 3px rgba(123,131,235,.35)`

**Both modes**
- `--rail-badge-ink: #131316` — badge text on the amber warning pill is dark ink in BOTH modes (Meridian rule).
- Radii: sm 4px · default 6px · lg 8px · pill 999px. Spacing on a 4px grid.
- Type: Geist (UI/body, 13–15px body, 18px/700 page titles), Geist Mono (counts, dates, kickers, tabular-nums). Print: black on white, no shadows.

## Screens / Views

### 1. Browse (hifi — match 2A/2B exactly)
Layout: fixed **230px left rail** + fluid main column.

**Rail** (`--rail` bg, 1px right border):
- Logo block (14px padding, bottom border): `VALOR★` — Geist Mono 19px/700, letter-spacing .06em, ★ in warning color; under it 10px uppercase tracked subtitle "MEDAL OF HONOR · PILOT 50".
- Nav (12px 10px padding, 2px gaps): items 13.5px/500, 9px 12px padding, radius 8. Active item: `--rail-raised` bg, text `--rail-text`, weight 600, `inset 2px 0 var(--accent)` left indicator. "Stories" carries a count badge: Geist Mono 10.5px/800, warning bg, **ink `--rail-badge-ink`**, pill radius, 1px 7px padding. "Saved views" carries a neutral badge (rail-raised bg).
- Section label "THEME GROUPS": 10px uppercase, .14em tracking, `--rail-subtle`, 14px 12px 6px padding. Four rows (13px): 3×15px radius-2 color bar in the group color + name + right-aligned mono count (61 / 21 / 28 / 37).
- Footer note card (10px margin, 9px 12px padding, radius 8): warning 12% tint bg, warning 30% border, warning text, 11px: "Pilot: 50 of 3,536 citations. Locations approximate."

**Main header** (surface bg, bottom border, 14px 26px): "Stories" 18px/700 + sub 12.5px `--text-subtle` "Find the stories by what they mean — 32 themes, every conflict, every branch." Right: 34px circular avatar, accent bg, white initials.

**Filter row** (14px 26px 0, 10px gaps): search input (max 320px, 1px border, radius 6, 8px 10px, shadow-sm, ⌕ glyph + placeholder in `--text-subtle`); three `.btn`-style dropdown buttons (Themes ▾ / Conflict ▾ / Branch ▾ — 12.5px/500, radius 6, shadow-sm); segmented fate control (one bordered radius-6 group, labels never wrap): **All** (accent-solid bg, white) | Survived | **★ Fell** (gold text).

**Count bar** (12px, `--text-subtle`): `50 of 50` (mono, 700, `--text`) " stories · 33 survived · **17 fell ★** (gold)" … right-aligned mono "1861 — 2010".

**Card grid**: `grid-template-columns: repeat(3, minmax(0,1fr))`, 16px gap, 16px 26px 24px padding. **Use minmax(0,1fr), not bare 1fr** — long unwrappable content must not widen tracks.

**Story card** (surface bg, 1px border, radius 8, shadow-md, 15px 17px padding, `box-sizing:border-box`, column flex, 10px gaps):
- Header row: 40px circle avatar (accent-tint bg, accent text, initials 14px/800) — swap to portrait photo when available; name 15px/700, one line, ellipsis (roster order: "Munro, Douglas Albert"); under it rank · branch 12px `--text-muted`, one line, ellipsis. Top-right: **theme-group indicator** — Meridian dept-seg pattern: 4 blocks 10×6px, radius 1, 2px gaps, on 3px `--surface-raised` pad (radius 4); each block lit in its group color when the story holds a theme in that group, else `--seg-off` (light `#e4e4e7` / dark `#313138`). Order: Deed, Person, Spirit, Aftermath.
- Meta line: Geist Mono 10.5px `--text-subtle`, uppercase: "WORLD WAR II · GUADALCANAL".
- Excerpt: 13px/1.55 `--text-muted`, 3-line clamp, from the citation's opening.
- Footer (single line, margin-top auto): **lead theme chip** — pill, 11px/600, 2px 9px, bg `color-mix(in srgb, <group color> 13%, transparent)`, text in group color, max-width ~185px with ellipsis; "+N" count 11px/600 `--text-subtle` for remaining themes; right-aligned **fate chip**: fallen = gold-tint pill "★ Fell" (11px/700), survived = neutral-tint pill "Survived".

### 2. Theme menu (structure per mockup 1B, Meridian skin)
Opens from the Themes button as a popover panel (surface bg, radius 8, shadow-lg, 1px border) over a dimmed grid. Four columns, one per group; each column headed by a 3px top rule in the group color + group name (11px/800, group color) + italic descriptor 11px `--text-subtle` ("what earned it / who they were / why it moves us / life beyond the medal"). 32 checkbox rows: 12px box (accent fill when checked), 12px label `--text-muted`, right mono count. Zero-count themes stay visible. Footer: italic hint "Counts update live as you stack filters.", ghost "Clear", primary "Show N stories" (accent-solid, radius 6). Mobile: bottom sheet with grabber, groups as accordions (+/–).

### 3. Active filters + saved views (per 1C)
A filter bar under the filter row: "ACTIVE" mono label; removable chips — theme chip in its group tint with ✕, search chip `⌕ "GRENADE"` neutral outline with ✕; "Clear all" text link. Right: "SAVED VIEWS" label + saved views as **outline pills** (Meridian pill radius) + dashed-border accent pill "+ Save current". Search matches render on cards as a quoted italic snippet with the hit term highlighted in accent tint (replaces the excerpt-only card body when search is active).

### 4. Story detail (per 1D)
Two-column: 340px meta rail (right border) + reading column.
- Meta rail: fate banner (gold 3px left rule + gold 8% tint, "★ FELL — 4 DECEMBER 2006" mono + place/age), SERVICE label + dashed-rule rows (mono 9.5px labels 96px wide / 12.5px values): rank, branch, unit, conflict, place, accredited, born. THEMES list: 3×15px group-color bar + theme name. Links: official record (cmohs.org ↗), print, show on map — accent color.
- Reading column: mono kicker "MEDAL OF HONOR · OFFICIAL CITATION — RENDERED VERBATIM" (accent); name display (Geist 700, ~28–34px); rank · branch · conflict sub; then the **citation verbatim and in full** — 16.5px / 1.7 / max 66ch, never truncated or editorialized (must comfortably carry the 4,587-char Benavidez citation). Footer note: italic source line + cmohs.org link.

### 5. Map view (per 1E)
List/Map toggle in the header (segmented, accent active). Leaflet + CARTO dark/light tiles matching mode. Pins: survived = 12px accent dot (white/dark ring); fallen = gold ★ glyph. Hover/tap card: surface popover with mono kicker, name, conflict · battle · fate, "READ THE STORY →" accent link. Legend chip bottom-left; zoom controls; disclaimer "Locations approximate — nearest named place."

### 6. Empty state (per 1F)
Centered: 44px top rule (border-strong), mono "NO MATCHES", 16px/600 headline naming the failing combination, 13px muted explanation ("The pilot holds 50 of 3,536 citations…"), secondary button "Remove last filter" + ghost "Clear all filters".

### 7. Mobile 390 (per 1I–1N)
Rail collapses; logo bar + MAP toggle on top; search full-width; filter buttons in a horizontally scrollable row; cards single column; theme menu = bottom sheet; detail = single column with fate banner above the citation; map = full-bleed with a story card docked at the bottom.

### 8. Print sheet (per 1H)
One story per Letter page, black on white: 3px top rule, mono header row (STORIES OF VALOR / MEDAL OF HONOR · OFFICIAL CITATION), name 26px/900 uppercase, mono sub, gold-ink fate line, hairline rule, citation 15.5px/1.7 verbatim, italic themes line, mono footer with source + recipient id. No chrome, no shadows, dept/theme colors reduced to ink.

## Interactions & Behavior
- Filters combine as AND across facets, OR within a facet; counts in menus update live against the current stack. URL should encode the full filter + search + view state (shareable).
- Search matches names, places, and full citation text; hits highlighted in cards (snippet) and detail (mark in accent tint).
- Buttons: hover = border-strong/text darken (primary: accent-hover); press = translateY(1px); loading = spinner replacing label; disabled = 45% opacity. Focus: ring replaces outline, **never removed** (`0 0 0 3px` accent alpha).
- Transitions ≤ 150ms ease on background/color/border/shadow; transform 60ms. Respect `prefers-reduced-motion`.
- Toasts: dark inverse panel (`#131316`) with leading icon, bottom-right — both modes.
- Skeletons: pulsing `--surface-raised` blocks mirroring card heights while data loads.
- Theme: auto-follows OS, manual toggle persisted (`data-theme` attr). Rail follows the mode (light rail in light, dark rail in dark).

## State Management
- `filters`: { themes[], conflicts[], branches[], battles[], fate: all|survived|fell, query }
- `view`: list | map; `theme`: light | dark | auto; `savedViews[]`: named filter snapshots (persisted).
- Derived: filtered story list, per-theme live counts, survived/fell tallies, year range.
- Data: stories (id, name, rank, branch, conflict, battle, place, lat/lng approx, survived, categories[1–4 of 32], citation verbatim, portrait?, born, accredited, unit). Sample data + the full 32-theme taxonomy: `stories.sample.json`.

## Assets
- Fonts: Geist + Geist Mono (Google Fonts CDN, or self-host as the Meridian source does).
- Icons: Meridian uses inline Lucide-style SVG paths (search, chevron, check). No emoji.
- Portraits: none yet — initials avatar is the designed fallback; cards must not reflow when photos arrive.
- Map tiles: CARTO light/dark via Leaflet.

## Files
- `MoH Stories Browser.dc.html` (project root) — full mockup canvas; **options 2A (light) and 2B (dark) are the chosen direction**; 1B–1N define structure for the remaining screens; 1T holds the sibling-language token sheet (superseded by `tokens.css` here).
- `StoryCardMeridian.dc.html` — the chosen story card, exact inline styles.
- `uploads/QUITTERS_Art_Dept_HQ_9.html` — Meridian source of truth (tokens + component CSS, §7/§8).
- This folder: `README.md`, `tokens.css`, `stories.sample.json`, `DESIGN_BRIEF.md` (original product brief).
