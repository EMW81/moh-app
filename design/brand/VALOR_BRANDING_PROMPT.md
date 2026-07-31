# Prompt: Apply VALOR branding to the MoH Stories app

You are working on **VALOR**, a Medal of Honor stories browser (light theme, zinc neutrals, Geist/Geist Mono type). A branding pass was just completed in a design tool. Apply it to the app as follows.

## Wordmark (site banner)
- The word **VALOR** set in **Geist Mono, weight 900, uppercase, letter-spacing 0.1em, line-height 0.72**, color **#04243b** (deep navy).
- Immediately after the R, a **gold five-point star** graphic (asset: `valor-star.png` — the rosette-tipped MoH star silhouette), sized to the cap height of the text (in the sidebar: text 30px / star 24px, baseline-aligned).
- Below it, a kicker: `MEDAL OF HONOR · PILOT 50` — Geist Mono 500, ~9px, letter-spacing 0.24em, color #a1a1aa.
- Reference render: `valor-banner-3a.png`.

## Branch-specific medals on story cards
There are **three distinct Medal of Honor designs**, one per branch:
- **Army** — eagle atop a VALOR bar, green laurel wreath (`moh-army.png`)
- **Navy** — anchor suspension, plain gold star (`moh-navy.png`)
- **Air Force** — thunderbolt suspension, Statue of Liberty medallion (`moh-airforce.png`, background already removed to transparent)

Each story card becomes a **3-column row**: portrait photo (left) · recipient info (middle) · the recipient's branch medal (far right).
- Medal column: ~148px wide, separated by a 1px #e4e4e7 left hairline; medal image ~104px tall, centered.
- Branch label beneath the medal: Geist Mono 900, ~10px, uppercase, letter-spacing 0.22em, color #04243b (`ARMY`, `NAVY`, `AIR FORCE`).
- Pick the medal by the recipient's `branch` field.
- Reference render: `stories-page-mockup-5a.png` (full page: sidebar wordmark + three example cards — Army/Parrott, Navy/Finn, Air Force/Sijan).

## Themes filter redesign (list + selected pills)
Replace the current Themes dropdown (oversized checkmark grid) with:
- **Popover**: 4 columns, one per theme group, each with a 3px colored top rule and title (Deed #c2410c, Person #7c3aed, Spirit #15803d, Aftermath #1d4ed8) plus an italic muted subtitle.
- **List rows**, not squares: 15px checkbox (1.5px #d4d4d8 border, 3px radius) · theme name (Geist 12.5px) · count right-aligned (Geist Mono 10.5px, #a1a1aa). Row hover: rgba(4,36,59,0.05).
- **Selected state**: checkbox fills #04243b with a white ✓, row gets rgba(4,36,59,0.06) background and 600-weight label.
- **Selected pills** render in a row under the filter toolbar: rounded-full chip, bg rgba(4,36,59,0.08), 1px rgba(4,36,59,0.18) border, navy 12px label, and a 16px circular ✕ button inside the pill that removes that filter (✕ hover: solid #04243b, white glyph). A "Clear all" text link follows the pills when any are active.
- Reference render: `themes-filter-mockup-6a.png`.

## Style tokens in play
- Navy brand ink: `#04243b` (wordmark, labels, active count pill)
- Zinc neutrals: page #f4f4f5, card #ffffff, borders #e4e4e7, body text #3f3f46, muted #71717a / #a1a1aa
- Theme chips: red tint `rgba(220,38,38,0.08)` with #b91c1c mono text; "★ Fell" status in #b45309
- Body/UI: Geist; anything label-like or numeric: Geist Mono

## Don'ts
- Don't recolor or restyle the medal artwork; it is the one polychrome element on the card.
- Don't use the wordmark star anywhere except after the R in VALOR.
- Keep exactly one medal per card — the branch match, never all three.
- Do NOT build circular "coin" crops of the medal medallions — that direction was rejected. Always show the full medal artwork.
