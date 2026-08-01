#!/usr/bin/env python3
"""Adjudication pass (Task 1, 2026-08-01) — deterministic stage.

Re-derives conflict for every conflict_uncertain record by mining the CITATION TEXT
(the pre-pass only used the structured year field, so 928 records with dates and
theaters spelled out in their citations fell through to Unknown).

Evidence rules, citation-text-only:
  1. action year = earliest year in action_date + citation, EXCLUDING years that follow
     "birth"/"born" or "issue"/"issued"/"g.o."/"presented" within a short window
     (issue dates postdate actions; birth years predate enlistment).
  2. era from that year (pre-pass year_signal, extended with 1914 Vera Cruz, 1915-20
     Haiti/Dominican windows, 1871 Korea).
  3. much richer keyword battery (Civil War: rebel/confederate/named battles/state
     volunteer regiments; Indian: named tribes; WWI: named offensives; WWII: named
     island campaigns; peacetime-interim: boiler/drowning-rescue language with no
     combat signal).
  4. year+keyword agree -> resolved, uncertain=False. Keyword unambiguous alone ->
     resolved. Year era alone -> resolved EXCEPT the frontier-era and 1898-1902 Navy
     peacetime traps, which need a combat keyword. Interim pattern -> "Interim Awards
     (Peacetime)". Anything else stays uncertain with a logged reason.

Output: data/adjudication/auto.json — {id: {conflict, conflict_uncertain,
conflict_reason, adjudicated: "auto-2026-08-01"}} — applied as an overlay by
merge_dataset.mjs. Pilot records are never touched (they carry no uncertain flags).
Residue (still uncertain) is listed in data/adjudication/residue.json for the manual
in-context pass.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from canonical import CONFLICTS as C

PEACETIME = "Interim Awards (Peacetime)"   # new label, logged for human review

YEAR_RE = re.compile(r"\b(18[5-9]\d|19\d\d|20[0-2]\d)\b")
EXCLUDE_BEFORE = re.compile(r"(?:birth|born|date of issue|issued|issuance|g\.o\.|general orders|presented|accredited)[^.]{0,60}$", re.I)

def action_years(rec):
    text = (rec.get("action_date") or "") + " . " + (rec.get("citation") or "")
    ys = []
    for m in YEAR_RE.finditer(text):
        prefix = text[max(0, m.start()-70):m.start()]
        if EXCLUDE_BEFORE.search(prefix):
            continue
        ys.append(int(m.group(1)))
    return sorted(set(ys))

def era_of(y):
    if y is None: return None
    if 1861 <= y <= 1865: return "civil"
    if y == 1871: return None            # Korea expedition vs frontier — keyword decides
    if 1866 <= y <= 1897: return "indian"
    if y == 1898: return "spanish"
    if 1899 <= y <= 1902: return "philippine"
    if y == 1914: return "mexico"
    if 1915 <= y <= 1920 and y not in (1917, 1918): return None  # Haiti/Dominican/interim — keyword decides
    if 1917 <= y <= 1918: return "ww1"
    if 1941 <= y <= 1945: return "ww2"
    if 1950 <= y <= 1953: return "korea"
    if 1961 <= y <= 1975: return "vietnam"
    if 2001 <= y <= 2014: return "afghanistan"
    return None

STATES = ("alabama|arkansas|connecticut|delaware|georgia|illinois|indiana|iowa|kansas|kentucky|"
          "louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|"
          "new hampshire|new jersey|new york|north carolina|ohio|pennsylvania|rhode island|"
          "tennessee|texas|vermont|virginia|west virginia|wisconsin")
VOL_UNIT = re.compile(r"\d+(?:st|d|nd|rd|th)\s+(?:%s)\s+(?:volunteer\s+)?(?:infantry|cavalry|artillery|volunteers)" % STATES)

def kw(text, unit):
    t = text
    u = unit.lower()
    def has(*ws): return any(w in t for w in ws)
    if has("vietnam", "republic of south vietnam"): return "vietnam", "vietnam keyword"
    if has("iraq", "baghdad", "fallujah", "ramadi", "al anbar"): return "iraq", "iraq keyword"
    if has("afghan", "kandahar", "kunar", "korengal", "wanat", "ganjgal"): return "afghanistan", "afghanistan keyword"
    if has("somalia", "mogadishu"): return "somalia", "somalia keyword"
    if has("boxer", "peking", "tientsin", "pei-tsang", "yang-tsun"): return "boxer", "boxer keyword"
    if has("vera cruz", "veracruz"): return "mexico", "vera cruz keyword"
    if has("haiti", "haitien", "caco"): return "haiti", "haiti keyword"
    if has("dominican", "santo domingo"): return "dominican", "dominican keyword"
    if has("nicaragua", "coco river", "ocotal"): return "nicaragua", "nicaragua keyword"
    if has("korea"):  return None, None  # era decides 1871 vs 1950s; handled by caller
    if has("rebel", "confederate", "c.s.s.", "css ", "secession", "fort fisher", "fort wagner",
           "mobile bay", "vicksburg", "petersburg", "gettysburg", "antietam", "chancellorsville",
           "appomattox", "shiloh", "chickamauga", "fredericksburg", "cold harbor", "spotsylvania",
           "fair oaks", "cedar creek", "five forks", "forts jackson and st. philip", "fort sumter",
           "colored troops", "army of the potomac"): return "civil", "civil-war keyword"
    if VOL_UNIT.search(t) or VOL_UNIT.search(u): return "civil", "state volunteer regiment"
    if has("indians", "apache", "sioux", "cheyenne", "comanche", "kiowa", "modoc", "nez perce",
           "chiricahua", "hostiles", "little big horn", "wounded knee", "white mountain"): return "indian", "tribe/frontier keyword"
    if has("spanish", "santiago de cuba", "cardenas", "cienfuegos", "el caney", "manila bay"): return "spanish", "spanish-war keyword"
    if has("insurgents", "insurrection", "philippine", "luzon", "samar", "mindanao"): return "philippine", "philippine keyword"
    if has("argonne", "meuse", "st. mihiel", "chateau-thierry", "belleau wood", "aisne",
           "verdun", "ypres", "german machinegun", "german machine gun"): return "ww1", "wwi keyword"
    if has("normandy", "okinawa", "iwo jima", "guadalcanal", "saipan", "leyte", "tarawa",
           "peleliu", "bougainville", "solomon islands", "anzio", "salerno", "bastogne",
           "remagen", "hurtgen", "kwajalein", "eniwetok", "corregidor", "bataan"): return "ww2", "wwii keyword"
    return None, None

INTERIM = re.compile(r"boiler|drowning|man overboard|overboard|wreck(?:ed)?|"
                     r"attempting to save|rescued? .{0,40}from the sea|heroism in rescuing|"
                     r"fire in the .{0,20}(?:magazine|bunker)|explosion of", re.I)
COMBAT = re.compile(r"enemy|rebel|battle|action against|under fire|assault|insurgent|hostile", re.I)

def adjudicate(rec):
    text = ((rec.get("action_place") or "") + " \n " + (rec.get("citation") or "")).lower()
    unit = rec.get("unit") or ""
    years = action_years(rec)
    y = years[0] if years else (rec.get("year") if rec.get("year") else None)
    era = era_of(y)
    k, kreason = kw(text, unit)
    is_sea = "navy" in (rec.get("branch") or "").lower() or "marine" in (rec.get("branch") or "").lower()
    interim = INTERIM.search(text) and not COMBAT.search(text)

    if "korea" in text:
        if y == 1871: return C["korea_expedition"], False, "korea + year 1871 in citation"
        if y and 1950 <= y <= 1953: return C["korea"], False, "korea + 1950s year in citation"
        if not y: return C["korea"], True, "korea keyword, no year — era undecided"
    if interim and (era is None or (is_sea and era in ("indian", "spanish", "philippine"))):
        return PEACETIME, False, f"non-combat rescue/accident language, no combat signal (year {y})"
    if k and era:
        if k == era: return C[k], False, f"adjudicated: year {y} in citation + {kreason}"
        return C[k], True, f"keyword ({kreason}) vs year {y} era {era} — keyword kept, still uncertain"
    if k: return C[k], False, f"adjudicated: {kreason} (no usable year)"
    if era:
        if era == "indian" and is_sea:
            return C["indian"], True, f"frontier-era ({y}) Navy/Marine, possibly peacetime — still uncertain"
        if era in ("spanish", "philippine") and is_sea and not COMBAT.search(text):
            return PEACETIME, False, f"navy {y}, no combat language — interim award"
        return C[era], False, f"adjudicated: year {y} in citation text (era {era})"
    return None, True, f"no year, no keyword after citation mining (years seen: {years[:4]})"

def main():
    stories = json.load(open(os.path.join(ROOT, "data", "stories.json")))
    pilot_ids = {r["id"] for r in stories[:50]}
    flagged = [r for r in stories if r.get("conflict_uncertain") and r["id"] not in pilot_ids]
    out, residue = {}, []
    for r in flagged:
        conflict, unc, reason = adjudicate(r)
        if conflict and not unc:
            out[r["id"]] = {"conflict": conflict, "conflict_uncertain": False,
                            "conflict_reason": reason, "adjudicated": "auto-2026-08-01"}
        else:
            if conflict and conflict != r["conflict"]:
                out[r["id"]] = {"conflict": conflict, "conflict_uncertain": True,
                                "conflict_reason": reason, "adjudicated": "auto-2026-08-01"}
            residue.append({"id": r["id"], "name": r["name"], "unit": r.get("unit",""),
                            "branch": r.get("branch",""), "year": r.get("year"),
                            "place": (r.get("action_place") or "")[:60],
                            "conflict": conflict or r["conflict"], "why": reason,
                            "citation": (r.get("citation") or "")[:420]})
    os.makedirs(os.path.join(ROOT, "data", "adjudication"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "data", "adjudication", "auto.json"), "w"), indent=1)
    json.dump(residue, open(os.path.join(ROOT, "data", "adjudication", "residue.json"), "w"), indent=1)
    from collections import Counter
    resolved = [v["conflict"] for v in out.values() if not v["conflict_uncertain"]]
    print(f"flagged {len(flagged)} | auto-resolved {len(resolved)} | residue {len(residue)}")
    print("resolved into:", Counter(resolved).most_common())

if __name__ == "__main__":
    main()
