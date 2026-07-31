# MOH Category Tagging — Fixed Per-Batch Prompt (Phase 5)

You are tagging Medal of Honor citations with themes from a **fixed 32-category
taxonomy**. You will receive a JSON array of records, each `{id, citation}` (some
also include rank/branch/conflict for context only). Return tags for every record.

## The ONE rule that governs everything
**Tag only what the citation TEXT itself supports.** The citation is the sole source
of truth. Never infer biography, motive, or outcome that the words do not state.
When in doubt, leave it off and lower the confidence.

## The 32 categories (use these strings EXACTLY — never rename, abbreviate, or invent)

**The Deed** (what earned it — tag FREELY from the action described):
- `The Assault` — attacking, charging, storming a position/enemy
- `The Last Stand` — holding a position against overwhelming odds, refusing to fall back
- `The Body on the Grenade` — smothering a grenade/explosive to shield others
- `The Rescue & Lifesaver` — pulling wounded/comrades to safety under fire
- `The Healer Under Fire` — medic/corpsman/surgeon treating wounded under fire
- `The Colors` — saving, carrying, or planting the flag/colors
- `One Against Many` — a lone fighter against a much larger force
- `The Raid` — a raid, infiltration, or behind-the-lines operation
- `Wings` — aerial combat / aviator action (pilot, aircrew)
- `The Sea` — naval action aboard or from ships / at sea
- `Unbroken in Captivity` — resisting as a POW / in captivity
- `The Rallying Point` — rallying, leading, inspiring troops forward

**The Person** (who they were — tag ONLY when the citation itself states the fact):
- `The Reluctant Warrior` — text states reluctance / conscientious objection
- `The New American / Immigrant's Debt` — text states immigrant/foreign-born status
- `The Trailblazer / The First` — text states a "first" (first to do X, first of a group)
- `The Boy (Too Young for This)` — text states very young age
- `The Career Warrior` — text states long/career service
- `The Citizen-Soldier` — text states civilian-turned-soldier / volunteer status
- `The Twice-Honored` — text references a second Medal of Honor / prior award

**The Spirit** (why it moves us — tag ONLY when EXPLICIT in the text):
- `Religious / Faith-Driven` — explicit prayer, faith, chaplain, "God"
- `Miraculous / Left for Dead` — explicit survival against impossible odds / left for dead
- `Greater Love` — explicitly shielding/saving others at his own peril (self-sacrifice for comrades)
- `Redemption / The Second Birth` — text states redemption / second chance
- `Brotherhood / No One Left Behind` — explicit refusal to leave the wounded/comrades
- `Duty & Country (Patriotic)` — explicit devotion to duty/country language
- `The Cost of War / Lament` — explicit language on the cost/grief of war

**The Aftermath** (life beyond the medal — tag ONLY when the citation STATES it):
- `The Fallen / Ultimate Sacrifice` — citation states death: posthumous, "gave his life",
  "mortally wounded", "killed", "at the cost of his life"
- `The Quiet Return` — text states a quiet return to civilian life
- `Belated Justice / The Long Vindication` — text states a long-delayed / upgraded award
- `The Forgotten Hero / Fall From Grace` — text states disgrace / being forgotten
- `The Wounded Warrior` — citation states the recipient was wounded (but survived)
- `The Epic Second Act` — text states a notable post-war life

## How to apply per group
- **Deed:** tag freely — these come straight from the action. Most records get 1-2 Deed tags.
- **Spirit:** require explicit textual evidence (a prayer, shielding a comrade with his body,
  refusing to leave the wounded). Do NOT read spirit into ordinary bravery.
- **Person / Aftermath:** require the citation to STATE the fact. `posthumously` or
  "gave his life" → `The Fallen / Ultimate Sacrifice`. "second Medal of Honor" →
  `The Twice-Honored`. "was wounded" (and lived) → `The Wounded Warrior`. If the fact is
  not in the text, leave it untagged — do NOT infer it from name, unit, or era.

## Count & confidence
- Assign **1–4** categories (the sweet spot is 1–3). Return **0** only if the citation is
  too sparse to support any tag — then set confidence `low` with a reason.
- Every record gets `confidence`: `high` | `medium` | `low`.
  - `high` — the tags are unmistakably supported by the text.
  - `medium` — reasonable but the text is terse or borderline.
  - `low` — sparse/ambiguous citation, or you are unsure. **Low requires a one-line `reason`.**

## Output (STRICT)
Return ONLY a JSON array, one object per input record, same order:
```json
[
  {"id":"john-c-sagelhurst","categories":["The Rescue & Lifesaver","The Assault"],"confidence":"high"},
  {"id":"jane-x-doe","categories":["The Sea"],"confidence":"low","reason":"one-line citation, little detail"}
]
```
Rules: `categories` is an array of 0–4 EXACT strings from the 32 above. `confidence` is one of
high/medium/low. Include `reason` only for `low`. No prose, no markdown fences, no extra keys.
