#!/usr/bin/env python3
"""Map-coverage rescue pass (2026-08-02): upgrade excluded (country/none) records to
APPROXIMATE campaign-level placement where the record honestly supports it.

Ladder per excluded record:
  1. deep re-scan of the FULL citation against the curated gazetteer (the first pass
     only scanned the first 500 chars) -> battlefield/locality precision
  2. campaign table: keyword -> campaign centroid (precision "campaign")
  3. theater inference: single-theater conflicts (Korea, Vietnam, Philippine-American,
     Boxer, Haiti, ...) or WWII split by enemy keyword (german -> ETO), WWI -> Western
     Front, Indian Campaigns -> US-state centroid from citation/place text
  4. truly nothing to go on -> stays off the map
Placements get a deterministic per-id jitter (±0.35°) so co-located campaign pins
don't stack into a false single point. Every result must pass the stage-2 theater
boxes. Output: data/geo/rescue.json (merge applies it after overrides.json).
"""
import hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_validate import CONFLICT_BOXES, inside

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAZ = json.load(open(os.path.join(ROOT, "data", "geo", "gazetteer.json")))
for g in GAZ: g["rx"] = re.compile(g["p"], re.I)

CAMPAIGN = [  # (regex, name, lat, lng, conflicts-or-None) — specific signals before theater fallback
    (r"\bbelgium\b|\bflanders\b", "Flanders, Belgium", 50.85, 2.9, ["World War I"]),
    (r"\bbelgium\b|\bardennes\b", "the Ardennes, Belgium", 50.25, 5.67, ["World War II"]),
    (r"\bitaly\b|\bitalian\b", "the Italian Front", 45.9, 11.9, ["World War I"]),
    (r"\bgermany\b", "Germany", 50.8, 9.5, ["World War I"]),
    (r"\bchina\b|\bburma\b", "the China-Burma-India theater", 24.0, 98.0, ["World War II"]),
    (r"\bmekong\b", "the Mekong Delta, Vietnam", 9.9, 105.8, ["Vietnam War"]),
    (r"demilitarized zone|\bdmz\b", "the Vietnamese DMZ", 16.9, 107.0, ["Vietnam War"]),
    (r"central highlands", "the Central Highlands, Vietnam", 13.9, 108.1, ["Vietnam War"]),
    (r"\bsouth korea\b", "South Korea", 36.6, 127.9, ["Korean War"]),
    (r"\bnorth korea\b", "North Korea", 39.5, 126.5, ["Korean War"]),
    (r"\bgermany\b", "Germany (1944-45 campaign)", 50.6, 9.0, ["World War II"]),
    (r"\bfrance\b", "France", 48.6, 2.7, ["World War II"]),
    (r"\bitaly\b", "the Italian campaign", 43.0, 12.5, ["World War II"]),
    (r"\bnew guinea\b", "New Guinea", -6.0, 145.0, ["World War II"]),
    (r"solomon islands", "the Solomon Islands", -9.0, 159.9, ["World War II"]),
    (r"marshall islands", "the Marshall Islands", 8.7, 167.7, ["World War II"]),
    (r"mariana", "the Mariana Islands", 15.1, 145.7, ["World War II"]),
    (r"\bcuba\b", "Cuba", 21.5, -79.5, ["Spanish-American War"]),
    (r"\bafghanistan\b", "Afghanistan", 34.0, 68.0, ["War on Terrorism (Afghanistan)"]),
    (r"\biraq\b", "Iraq", 33.3, 43.7, ["War on Terrorism (Iraq)"]),
]
THEATER = {  # conflict alone narrows to a single theater
    "Korean War": ("Korea", 37.8, 127.2),
    "Vietnam War": ("Vietnam", 13.8, 108.3),
    "Philippine-American War": ("Luzon, Philippines", 15.5, 121.0),
    "China Relief Expedition (Boxer Rebellion)": ("the Peking-Tientsin corridor, China", 39.3, 116.9),
    "Mexican Campaign (Vera Cruz)": ("Veracruz, Mexico", 19.19, -96.15),
    "Haitian Campaign": ("Haiti", 19.0, -72.7),
    "Dominican Campaign": ("the Dominican Republic", 18.8, -70.2),
    "Nicaraguan Campaign": ("Nicaragua", 12.9, -85.9),
    "War on Terrorism (Afghanistan)": ("Afghanistan", 34.0, 68.0),
    "War on Terrorism (Iraq)": ("Iraq", 33.3, 43.7),
    "World War I": ("the Western Front, France", 49.2, 4.0),  # AEF overwhelmingly France
    "Korean Expedition (1871)": ("Ganghwa, Korea", 37.70, 126.44),
}
STATES = {"montana":(46.9,-110.4),"arizona":(34.3,-111.7),"new mexico":(34.4,-106.1),
 "texas":(31.5,-99.3),"south dakota":(44.4,-100.2),"north dakota":(47.4,-100.5),
 "kansas":(38.5,-98.3),"colorado":(39.0,-105.5),"oklahoma":(35.6,-97.5),
 "oregon":(43.9,-120.6),"idaho":(44.4,-114.6),"wyoming":(43.0,-107.5),
 "nebraska":(41.5,-99.8),"minnesota":(46.3,-94.3),"california":(37.2,-119.3),
 "nevada":(39.6,-116.6),"utah":(39.3,-111.7),"washington":(47.4,-120.5)}

def jitter(rid, span=0.35):
    h = hashlib.md5(rid.encode()).digest()
    return ((h[0]/255-0.5)*2*span, (h[1]/255-0.5)*2*span)

def boxes_ok(conflict, lat, lng):
    keys = CONFLICT_BOXES.get(conflict)
    return (not keys) or any(inside({"lat":lat,"lng":lng}, k) for k in keys)

def main():
    stories = json.load(open(os.path.join(ROOT, "data", "stories.json")))
    # idempotent: targets are defined by the PRE-rescue pipeline output (overrides.json),
    # not the merged dataset — re-runs always re-derive the full rescue set
    overrides = json.load(open(os.path.join(ROOT, "data", "geo", "overrides.json")))
    targets = [r for r in stories if overrides.get(r["id"], {}).get("geo_precision") in ("country", "none")]
    out, stats = {}, {"deep_gazetteer":0,"campaign":0,"theater":0,"state":0,"still_off":0,"box_reject":0}
    for r in targets:
        text = " | ".join(filter(None,[r.get("battle"), r.get("action_place"), r.get("citation")])).lower()
        placed = None
        for g in GAZ:  # 1. deep full-citation gazetteer scan
            if g["rx"].search(text) and not ("c" in g and r["conflict"] not in g["c"]):
                placed = (g["n"], g["lat"], g["lng"], g["prec"], "deep_gazetteer"); break
        if not placed:  # 2. campaign table
            for pat, name, la, ln, confs in CAMPAIGN:
                if re.search(pat, text) and (confs is None or r["conflict"] in confs):
                    placed = (name, la, ln, "campaign", "campaign"); break
        if not placed and r["conflict"] == "World War II" and re.search(r"\bgerman", text):
            placed = ("the European Theater", 50.0, 7.5, "campaign", "theater")
        if not placed and r["conflict"] == "Indian Campaigns":  # 3b. state centroid
            for st,(la,ln) in STATES.items():
                if re.search(r"\b"+st+r"\b", text):
                    placed = (st.title()+" (frontier campaigns)", la, ln, "region", "state"); break
        if not placed and r["conflict"] in THEATER:  # 3. single-theater conflict
            name, la, ln = THEATER[r["conflict"]]
            placed = (name, la, ln, "campaign", "theater")
        if placed:
            name, la, ln, prec, how = placed
            if prec in ("campaign", "region"):
                dj, dk = jitter(r["id"]); la, ln = round(la+dj, 3), round(ln+dk, 3)
            if boxes_ok(r["conflict"], la, ln):
                out[r["id"]] = {"coords":{"lat":la,"lng":ln},"geo_place":name,"geo_precision":prec}
                stats[how] += 1
                continue
            stats["box_reject"] += 1
        stats["still_off"] += 1
    json.dump(out, open(os.path.join(ROOT,"data","geo","rescue.json"),"w"))
    print(f"targets {len(targets)}:", stats)

if __name__ == "__main__":
    main()
