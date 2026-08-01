#!/usr/bin/env python3
"""Map-accuracy stages 3-4: recompute coordinates for the full corpus.

Pipeline per record (first hit wins):
  1. curated gazetteer (data/geo/gazetteer.json) — famous battles, exact/battlefield
  2. place text: citation "Place and date:" line (Army format) beats action_place;
     action_place is distrusted when it smells like a US street address while the
     conflict is overseas (the CORGIS pollution class)
  3. Nominatim geocode of the cleaned place string — 1 req/s, proper User-Agent,
     every response cached in data/geocache.json (re-runs are free)
  4. post-check: new coords must pass the stage-2 bounding boxes, else discarded
Precision: exact | battlefield | locality | region | country | none.
Output: data/geo/overrides.json  {id: {coords, geo_place, geo_precision}}
Usage: geo_fix.py [--offline]   (offline = no network; queue report only)
"""
import json, os, re, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_validate import BOX, CONFLICT_BOXES, inside

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "moh-stories-browser/1.0 (everymedal.org; github.com/EMW81/moh-app)"
CACHE_PATH = os.path.join(ROOT, "data", "geocache.json")
OVERSEAS = set(CONFLICT_BOXES) - {"U.S. Civil War", "Indian Campaigns"}

GAZ = json.load(open(os.path.join(ROOT, "data", "geo", "gazetteer.json")))
for g in GAZ: g["rx"] = re.compile(g["p"], re.I)

STREET = re.compile(r"\d{2,5} [A-Z]|\b(street|avenue|drive|lane|boulevard|court|circle)\b|, [A-Z]{2} \d{5}", re.I)
PLACE_DATE = re.compile(r"place and date:\s*(.+?)(?:[,.;]?\s*\d{1,2}(?:-\d{1,2})?\s+\w+\s+\d{4}|[,.;]\s*\d{4}\b|\.\s)", re.I)

def cache_load():
    try: return json.load(open(CACHE_PATH))
    except Exception: return {}

def clean_place(p):
    p = re.sub(r"^\s*(near|at|vicinity of|in)\s+", "", p.strip(), flags=re.I)
    p = re.sub(r"\s+", " ", p).strip(" ,.;")
    return p

def candidate_place(r):
    cit = r.get("citation") or ""
    m = PLACE_DATE.search(cit)
    if m:
        c = clean_place(m.group(1))
        if 3 <= len(c) <= 90 and "?" not in c: return c
    ap = (r.get("action_place") or "").strip()
    if ap and "?" not in ap:
        polluted = r["conflict"] in OVERSEAS and (STREET.search(ap) or ap.endswith("USA"))
        if not polluted: return clean_place(ap)
    return None

PREC_BY_TYPE = {
    "city":"locality","town":"locality","village":"locality","hamlet":"locality",
    "suburb":"locality","island":"locality","islet":"locality","locality":"locality",
    "peak":"battlefield","military":"battlefield","fort":"battlefield","historic":"battlefield",
    "county":"region","state":"region","region":"region","province":"region",
    "archipelago":"region","state_district":"region","municipality":"locality",
    "country":"country",
}

def nominatim(q, cache, offline):
    if q in cache: return cache[q]
    if offline: return None
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 1, "accept-language": "en"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            data = json.loads(f.read().decode())
    except Exception as e:
        data = {"__error__": str(e)[:100]}
    cache[q] = data
    json.dump(cache, open(CACHE_PATH, "w"))
    time.sleep(1.05)
    return data

def boxes_ok(r, lat, lng):
    keys = CONFLICT_BOXES.get(r["conflict"])
    if not keys: return True
    return any(inside({"lat": lat, "lng": lng}, k) for k in keys)

def main():
    offline = "--offline" in sys.argv
    stories = json.load(open(os.path.join(ROOT, "data", "stories.json")))
    cache = cache_load()
    out, stats = {}, {"gazetteer":0,"nominatim":0,"none":0,"discarded_box":0,"queue":0}
    queue = set()
    for r in stories:
        text = " | ".join(filter(None, [r.get("battle"), r.get("action_place"), (r.get("citation") or "")[:500]])).lower()
        hit = None
        for g in GAZ:
            if g["rx"].search(text):
                if "c" in g and r["conflict"] not in g["c"]: continue
                hit = g; break
        if hit:
            out[r["id"]] = {"coords":{"lat":hit["lat"],"lng":hit["lng"]},
                            "geo_place":hit["n"], "geo_precision":hit["prec"]}
            stats["gazetteer"] += 1
            continue
        q = candidate_place(r)
        if q:
            res = nominatim(q, cache, offline)
            if res is None:
                queue.add(q); stats["queue"] += 1
                continue
            if isinstance(res, list) and res:
                item = res[0]
                lat, lng = float(item["lat"]), float(item["lon"])
                prec = PREC_BY_TYPE.get(item.get("addresstype") or item.get("type"), "locality")
                if item.get("type") in ("administrative",) and item.get("place_rank", 30) <= 8:
                    prec = "country"
                if boxes_ok(r, lat, lng):
                    name = q if len(q) <= 60 else q[:57]+"…"
                    out[r["id"]] = {"coords":{"lat":round(lat,4),"lng":round(lng,4)},
                                    "geo_place":name, "geo_precision":prec}
                    stats["nominatim"] += 1
                    continue
                stats["discarded_box"] += 1
        out[r["id"]] = {"coords":None, "geo_place":None, "geo_precision":"none"}
        stats["none"] += 1
    json.dump(out, open(os.path.join(ROOT,"data","geo","overrides.json"),"w"))
    print(stats)
    if offline and queue:
        json.dump(sorted(queue), open(os.path.join(ROOT,"data","geo","queue.json"),"w"), indent=0)
        print(f"unique nominatim queries pending: {len(queue)}")

if __name__ == "__main__":
    main()
