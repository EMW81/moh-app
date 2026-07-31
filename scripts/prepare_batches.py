#!/usr/bin/env python3
"""Phase-5 PRE-PASS (deterministic).

Transform data/medal_of_honor.json (CORGIS, 3,475 records) into chunk files of 250
records each at data/chunks/chunk_NN.json.

Per record we DERIVE (no LLM here):
  - conflict            from action year + location keywords + citation text
  - conflict_uncertain  True when signals disagree, or no signal at all
  - survived            from citation posthumous-language heuristic
  - survived_confidence high/medium/low
and CARRY id, name, rank, branch, unit, action_date, year, action_place, coords,
citation, accredited_to, born, cmohs_link.

The 50 curated pilot records (data/pilot50.json) are SKIPPED here — never overwritten.
Records are matched to the pilot by the stable cmohs recipient-detail number.

Run:  python3 scripts/prepare_batches.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from canonical import CONFLICTS as C

SRC = os.path.join(ROOT, "data", "medal_of_honor.json")
PILOT = os.path.join(ROOT, "data", "pilot50.json")
OUTDIR = os.path.join(ROOT, "data", "chunks")
CHUNK = 250

def cmohs_num(link):
    m = re.search(r"recipient-detail/(\d+)/", link or "")
    return m.group(1) if m else None

def slugify(s):
    s = re.sub(r"[.’']", "", (s or "").lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def make_id(name, num, seen):
    # "Last, First M." -> "first-m-last" (matches pilot style closely)
    if "," in name:
        last, first = name.split(",", 1)
        first = re.sub(r"\b(dr)\b\.?", "", first, flags=re.I)
        base = slugify(first + " " + last)
    else:
        base = slugify(name)
    if not base:
        base = "moh-" + (num or "x")
    cid = base
    if cid in seen:
        cid = f"{base}-{num}" if num else f"{base}-{len(seen)}"
    seen.add(cid)
    return cid

# ---------- conflict derivation ----------
def year_signal(y):
    if y is None or y <= 0: return None
    if 1861 <= y <= 1865: return "civil"
    if 1866 <= y <= 1897: return "indian"
    if y == 1898: return "spanish"
    if 1899 <= y <= 1902: return "philippine"
    if 1917 <= y <= 1918: return "ww1"
    if 1941 <= y <= 1945: return "ww2"
    if 1950 <= y <= 1953: return "korea"
    if 1961 <= y <= 1975: return "vietnam"
    if 2001 <= y <= 2014: return "afghanistan"  # GWOT default; iraq split by keyword
    return None  # interwar / peacetime gaps

def keyword_signal(text, y):
    t = text
    def has(*ws): return any(w in t for w in ws)
    # unambiguous modern theaters
    if has("vietnam"): return "vietnam"
    if has("iraq", "baghdad", "fallujah", "al anbar", "ramadi"): return "iraq"
    if has("afghan", "kandahar", "kunar", "korengal", "wanat"): return "afghanistan"
    if has("somalia", "mogadishu"): return "somalia"
    if has("cuba", "santiago de cuba", "guantanamo"): return "spanish"
    if has("vera cruz", "veracruz"): return "mexico"
    if has("haiti", "haitien", "port-au-prince"): return "haiti"
    if has("dominican", "santo domingo"): return "dominican"
    if has("nicaragua"): return "nicaragua"
    # year-disambiguated theaters
    if has("korea"):
        if y == 1871: return "korea_expedition"
        if y is None or 1950 <= y <= 1953: return "korea"
        return "korea"
    if has("philippine", "luzon", "samar", "mindanao", "manila"):
        if y and 1941 <= y <= 1945: return "ww2"
        return "philippine"
    if has("china", "peking", "peiking", "tientsin", "boxer"):
        if y and 1941 <= y <= 1945: return "ww2"
        return "boxer"
    return None

def derive_conflict(rec):
    aw = rec.get("awarded", {})
    y = aw.get("date", {}).get("year")
    y = y if isinstance(y, int) and y > 0 else None
    place = (aw.get("location", {}) or {}).get("name", "") or ""
    cit = aw.get("citation", "") or ""
    text = (place + " \n " + cit).lower()
    org = (rec.get("military record", {}) or {}).get("organization", "") or ""
    is_sea = ("navy" in org.lower()) or ("marine" in org.lower())

    ys = year_signal(y)
    ks = keyword_signal(text, y)

    if ks and ys:
        if ks == ys:
            return C[ks], False, "year+keyword agree"
        return C[ks], True, f"year says {ys}, keyword says {ks}"
    if ks and not ys:
        return C[ks], False, "keyword only"
    if ys and not ks:
        # peacetime-naval trap: Navy/Marine awards in the 1866-1897 frontier era were
        # often non-combat; flag those uncertain rather than mislabel "Indian Campaigns".
        if ys == "indian" and is_sea:
            return C["indian"], True, "frontier-era Navy/Marine, possibly peacetime"
        return C[ys], False, "year era only"
    return C["unknown"], True, "no year or keyword signal"

# ---------- survived heuristic ----------
STRONG = re.compile(
    r"gave (?:up )?(?:his|her) life|laid down (?:his|her) life|"
    r"at the (?:cost|sacrifice) of (?:his|her)(?: own)? life|"
    r"mortally wounded|posthumous|killed in action|(?:the )?supreme sacrifice|"
    r"sacrific(?:ed|ing) (?:his|her|him)self|was killed|was slain|"
    r"fell mortally|died of (?:his |her )?wounds", re.I)
AMBIG = re.compile(r"\bdied\b|until (?:his|her) death|his death|her death|\bdying\b", re.I)

def derive_survived(cit):
    cit = cit or ""
    if STRONG.search(cit):
        return False, "high", "explicit posthumous/mortal language"
    if AMBIG.search(cit):
        return False, "low", "ambiguous death language"
    if len(cit) < 40:
        return True, "medium", "short citation, no death language"
    return True, "high", ""

# ---------- carry fields ----------
def carry(rec, cid, num):
    aw = rec.get("awarded", {})
    mr = rec.get("military record", {}) or {}
    loc = aw.get("location", {}) or {}
    y = aw.get("date", {}).get("year")
    y = y if isinstance(y, int) and y > 0 else None
    full = aw.get("date", {}).get("full")
    unit = ", ".join([x for x in [mr.get("company"), mr.get("division")] if x])
    lat, lng = loc.get("latitude"), loc.get("longitude")
    conflict, cuncertain, creason = derive_conflict(rec)
    survived, sconf, sreason = derive_survived(aw.get("citation"))
    return {
        "id": cid,
        "cmohs_num": num,
        "name": rec.get("name", ""),
        "rank": mr.get("rank", ""),
        "branch": mr.get("organization", ""),
        "unit": unit,
        "conflict": conflict,
        "conflict_uncertain": cuncertain,
        "conflict_reason": creason,
        "year": y,
        "action_date": full if (full and y) else None,
        "action_place": loc.get("name", ""),
        "coords": {"lat": lat, "lng": lng} if (lat is not None and lng is not None) else None,
        "survived": survived,
        "survived_confidence": sconf,
        "survived_reason": sreason,
        "accredited_to": aw.get("accredited to", ""),
        "born": (rec.get("birth", {}) or {}).get("location name", ""),
        "citation": aw.get("citation", "") or "",
        "cmohs_link": (rec.get("metadata", {}) or {}).get("link", ""),
    }

def main():
    src = json.load(open(SRC))
    pilot = json.load(open(PILOT))["recipients"]
    pilot_nums = {cmohs_num(p.get("cmohs_link")) for p in pilot}
    pilot_nums.discard(None)

    os.makedirs(OUTDIR, exist_ok=True)
    # clear any stale chunk files (deterministic rebuild)
    for f in os.listdir(OUTDIR):
        if re.match(r"chunk_\d+\.json$", f):
            os.remove(os.path.join(OUTDIR, f))

    seen = set()
    out = []
    skipped = 0
    stats = {"conflict_counts": {}, "uncertain": 0, "no_year": 0,
             "survived_false": 0, "surv_conf": {"high": 0, "medium": 0, "low": 0}}
    for rec in src:
        num = cmohs_num((rec.get("metadata", {}) or {}).get("link", ""))
        if num and num in pilot_nums:
            skipped += 1
            continue
        cid = make_id(rec.get("name", ""), num, seen)
        r = carry(rec, cid, num)
        out.append(r)
        stats["conflict_counts"][r["conflict"]] = stats["conflict_counts"].get(r["conflict"], 0) + 1
        if r["conflict_uncertain"]: stats["uncertain"] += 1
        if r["year"] is None: stats["no_year"] += 1
        if not r["survived"]: stats["survived_false"] += 1
        stats["surv_conf"][r["survived_confidence"]] += 1

    nchunks = (len(out) + CHUNK - 1) // CHUNK
    for i in range(nchunks):
        part = out[i*CHUNK:(i+1)*CHUNK]
        path = os.path.join(OUTDIR, f"chunk_{i+1:02d}.json")
        json.dump({"chunk": i+1, "count": len(part), "records": part},
                  open(path, "w"), indent=1, ensure_ascii=False)

    print(f"source records:      {len(src)}")
    print(f"skipped pilot:       {skipped}")
    print(f"prepared records:    {len(out)}")
    print(f"chunks written:      {nchunks}  (chunk_01..chunk_{nchunks:02d}, {CHUNK}/chunk)")
    print(f"\nconflict_uncertain:  {stats['uncertain']}  ({100*stats['uncertain']//len(out)}%)")
    print(f"  of which no-year:  {stats['no_year']} records had no action year")
    print(f"survived=False:      {stats['survived_false']}")
    print(f"survived_confidence: {stats['surv_conf']}")
    print("\nconflict distribution:")
    for k, v in sorted(stats["conflict_counts"].items(), key=lambda kv: -kv[1]):
        print(f"  {v:5}  {k}")

if __name__ == "__main__":
    main()
