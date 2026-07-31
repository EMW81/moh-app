"""Shared constants for the Phase-5 tagging pipeline.

The 32 canonical category names are Darrin's taxonomy (CLAUDE.md) — verbatim,
never renamed. Any tagger output must match one of these strings EXACTLY.
"""

CATEGORIES = [
    # The Deed (what earned it)
    "The Assault",
    "The Last Stand",
    "The Body on the Grenade",
    "The Rescue & Lifesaver",
    "The Healer Under Fire",
    "The Colors",
    "One Against Many",
    "The Raid",
    "Wings",
    "The Sea",
    "Unbroken in Captivity",
    "The Rallying Point",
    # The Person (who they were)
    "The Reluctant Warrior",
    "The New American / Immigrant's Debt",
    "The Trailblazer / The First",
    "The Boy (Too Young for This)",
    "The Career Warrior",
    "The Citizen-Soldier",
    "The Twice-Honored",
    # The Spirit (why it moves us)
    "Religious / Faith-Driven",
    "Miraculous / Left for Dead",
    "Greater Love",
    "Redemption / The Second Birth",
    "Brotherhood / No One Left Behind",
    "Duty & Country (Patriotic)",
    "The Cost of War / Lament",
    # The Aftermath (life beyond the medal)
    "The Fallen / Ultimate Sacrifice",
    "The Quiet Return",
    "Belated Justice / The Long Vindication",
    "The Forgotten Hero / Fall From Grace",
    "The Wounded Warrior",
    "The Epic Second Act",
]

CATEGORY_SET = set(CATEGORIES)
assert len(CATEGORIES) == 32, "expected 32 canonical categories"

# Canonical conflict labels (aligned with the curated pilot50 set, plus a few the
# full dataset needs). Used by prepare_batches for deterministic conflict labels.
CONFLICTS = {
    "civil": "U.S. Civil War",
    "indian": "Indian Campaigns",
    "spanish": "Spanish-American War",
    "philippine": "Philippine-American War",
    "boxer": "China Relief Expedition (Boxer Rebellion)",
    "mexico": "Mexican Campaign (Vera Cruz)",
    "haiti": "Haitian Campaign",
    "dominican": "Dominican Campaign",
    "nicaragua": "Nicaraguan Campaign",
    "ww1": "World War I",
    "ww2": "World War II",
    "korea": "Korean War",
    "korea_expedition": "Korean Expedition (1871)",
    "vietnam": "Vietnam War",
    "somalia": "Somalia (Operation Restore Hope)",
    "iraq": "War on Terrorism (Iraq)",
    "afghanistan": "War on Terrorism (Afghanistan)",
    "unknown": "Unknown",
}
