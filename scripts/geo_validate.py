#!/usr/bin/env python3
"""Map-accuracy stage 2: flag records whose coords are inconsistent with their
conflict theater and/or action_place country keywords (bounding-box check).
Run pre-fix (inventory) and post-fix (QA gate: should be ~zero).
Usage: python3 scripts/geo_validate.py [--json data/geo/flags.json]
"""
import json, os, re, sys

BOX = {  # (lat_min, lat_max, lng_min, lng_max)
    "us":        (24, 50, -125, -66),
    "hawaii":    (18, 23, -161, -154),
    "alaska":    (51, 72, -170, -129),
    "france":    (42, 51.5, -5.5, 8.5),
    "belgium":   (49.4, 51.6, 2.4, 6.5),
    "germany":   (47, 55, 5.5, 15.2),
    "italy":     (36, 47.5, 6, 19),
    "uk":        (49, 61, -8.5, 2),
    "n_africa":  (20, 38, -12, 12),
    "philippines":(4.5, 21.5, 116, 127),
    "japan":     (24, 46, 122, 146),
    "korea":     (33, 43.5, 124, 131),
    "vietnam":   (8, 24, 100, 110),
    "china":     (18, 54, 73, 135),
    "cuba":      (19.5, 23.5, -85.5, -74),
    "caribbean": (17, 24, -85.5, -64),
    "mexico":    (14, 33, -118, -86),
    "haiti":     (17.9, 20.2, -74.6, -71.6),
    "domrep":    (17.4, 20, -72.1, -68.2),
    "nicaragua": (10.7, 15.1, -87.8, -82.5),
    "somalia":   (-2, 12.2, 40, 51.5),
    "afghanistan":(29, 39, 60, 75),
    "iraq":      (29, 37.5, 38.5, 48.8),
    "pacific":   (-15, 30, 130, 180),
    "pacific_e": (-15, 30, -180, -150),
    "png_solomons":(-12, 0, 140, 163),
    "samoa":     (-14.5, -13, -173, -171),
    "chile":     (-56, -17, -76, -66),
    "greenland": (59, 84, -75, -10),
}
CONFLICT_BOXES = {
    "U.S. Civil War": ["us"],
    "Indian Campaigns": ["us"],
    "Korean Expedition (1871)": ["korea"],
    "Spanish-American War": ["cuba", "caribbean", "philippines"],
    "Philippine-American War": ["philippines"],
    "China Relief Expedition (Boxer Rebellion)": ["china"],
    "Mexican Campaign (Vera Cruz)": ["mexico"],
    "Haitian Campaign": ["haiti"],
    "Dominican Campaign": ["domrep"],
    "Nicaraguan Campaign": ["nicaragua"],
    "World War I": ["france", "belgium", "germany", "italy", "uk"],
    "World War II": ["france", "belgium", "germany", "italy", "uk", "n_africa",
                     "philippines", "japan", "pacific", "pacific_e", "png_solomons", "hawaii", "alaska"],
    "Korean War": ["korea"],
    "Vietnam War": ["vietnam"],
    "Somalia (Operation Restore Hope)": ["somalia"],
    "War on Terrorism (Afghanistan)": ["afghanistan"],
    "War on Terrorism (Iraq)": ["iraq"],
}
PLACE_KEYS = [  # action_place keyword -> box (checked in addition to conflict)
    (r"\bfrance\b", "france"), (r"\bbelgium\b", "belgium"), (r"\bgermany\b", "germany"),
    (r"\bitaly\b", "italy"), (r"\bphilippine", "philippines"), (r"\bjapan\b", "japan"),
    (r"\bkorea\b", "korea"), (r"\bvietnam\b", "vietnam"), (r"\bchina\b", "china"),
    (r"\bcuba\b", "cuba"), (r"(?<!new )\bmexico\b", "mexico"), (r"\bhaiti\b", "haiti"),
    (r"\bnicaragua\b", "nicaragua"), (r"\bsomalia\b", "somalia"),
    (r"\bafghanistan\b", "afghanistan"), (r"\biraq\b", "iraq"), (r"\bchile\b", "chile"),
    (r"\bgreenland\b", "greenland"), (r"\bsamoa\b", "samoa"),
]

def inside(c, key):
    a, b, x, y = BOX[key]
    return a <= c["lat"] <= b and x <= c["lng"] <= y

def validate(stories):
    flags = []
    for r in stories:
        c = r.get("coords")
        if not c or c.get("lat") is None:
            flags.append({"id": r["id"], "why": "null coords"}); continue
        # curated gazetteer pins (exact/battlefield) are hand-verified and legitimately
        # include theaters the boxes can't model (Kearsarge off Cherbourg, Midway,
        # Attu past the antimeridian) — and action_place is often polluted anyway.
        if r.get("geo_place") and r.get("geo_precision") in ("exact", "battlefield"):
            continue
        boxes = CONFLICT_BOXES.get(r["conflict"])
        place = (r.get("action_place") or "").lower()
        pboxes = [k for pat, k in PLACE_KEYS if re.search(pat, place)]
        why = []
        if boxes and not any(inside(c, k) for k in boxes):
            why.append(f"outside {r['conflict']} theater")
        if pboxes and not any(inside(c, k) for k in pboxes):
            why.append(f"outside place-keyword box ({','.join(pboxes)})")
        if why:
            flags.append({"id": r["id"], "conflict": r["conflict"], "coords": c,
                          "place": (r.get("action_place") or "")[:60], "why": "; ".join(why)})
    return flags

if __name__ == "__main__":
    stories = json.load(open("data/stories.json"))
    flags = validate(stories)
    os.makedirs("data/geo", exist_ok=True)
    out = "data/geo/flags.json"
    if "--json" in sys.argv: out = sys.argv[sys.argv.index("--json")+1]
    json.dump(flags, open(out, "w"), indent=1)
    from collections import Counter
    print(f"{len(flags)} flagged of {len(stories)}")
    print(Counter(f["why"].split(";")[0] for f in flags).most_common(10))
