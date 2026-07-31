#!/usr/bin/env python3
"""Phase-5 batch-loop core: validate + merge + fingerprint one tagged chunk.

Subcommands:
  status                 show manifest: which chunks are done / pending / stale
  check   NN             exit 0 if chunk NN is already done (input unchanged), else 1
  merge   NN TAGS.json   validate TAGS.json against chunk_NN, merge -> data/tagged/,
                         record a sha256 fingerprint of the chunk input in the manifest

Resumability: the manifest stores the sha256 of each chunk's INPUT file. `check`
returns done only when that hash still matches, so re-runs skip completed chunks and
a changed input forces a re-tag.

Validation (a chunk is rejected, nothing written, on any failure):
  - valid JSON array, one entry per chunk record, ids match exactly (full coverage)
  - categories: 0-4 items, each EXACTLY one of the 32 canonical names
  - confidence in {high, medium, low}; low REQUIRES a non-empty reason
"""
import json, os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from canonical import CATEGORY_SET

CHUNKDIR = os.path.join(ROOT, "data", "chunks")
TAGDIR = os.path.join(ROOT, "data", "tagged")
MANIFEST = os.path.join(TAGDIR, "_manifest.json")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

def load_manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST))
    return {"chunks": {}}

def save_manifest(m):
    os.makedirs(TAGDIR, exist_ok=True)
    json.dump(m, open(MANIFEST, "w"), indent=1)
    open(MANIFEST, "a").write("\n")

def chunk_path(nn):
    return os.path.join(CHUNKDIR, f"chunk_{int(nn):02d}.json")

def validate(nn, tags):
    """Return (ok, errors, by_id) for tags against chunk NN."""
    errs = []
    chunk = json.load(open(chunk_path(nn)))
    recs = chunk["records"]
    chunk_ids = [r["id"] for r in recs]
    chunk_id_set = set(chunk_ids)
    if not isinstance(tags, list):
        return False, ["tags is not a JSON array"], {}
    by_id = {}
    for i, t in enumerate(tags):
        if not isinstance(t, dict) or "id" not in t:
            errs.append(f"[{i}] not an object with id"); continue
        tid = t["id"]
        if tid not in chunk_id_set:
            errs.append(f"[{i}] id '{tid}' not in chunk {nn}")
        if tid in by_id:
            errs.append(f"[{i}] duplicate id '{tid}'")
        cats = t.get("categories", [])
        if not isinstance(cats, list):
            errs.append(f"{tid}: categories not a list")
            cats = []
        if len(cats) > 4:
            errs.append(f"{tid}: {len(cats)} categories (max 4)")
        for c in cats:
            if c not in CATEGORY_SET:
                errs.append(f"{tid}: non-canonical category {c!r}")
        conf = t.get("confidence")
        if conf not in ("high", "medium", "low"):
            errs.append(f"{tid}: bad confidence {conf!r}")
        if conf == "low" and not (t.get("reason") or "").strip():
            errs.append(f"{tid}: low confidence requires a reason")
        by_id[tid] = t
    missing = chunk_id_set - set(by_id)
    if missing:
        errs.append(f"missing {len(missing)} ids (e.g. {sorted(missing)[:3]})")
    return (len(errs) == 0), errs, by_id

def cmd_merge(nn, tagfile):
    tags = json.load(open(tagfile))
    ok, errs, by_id = validate(nn, tags)
    if not ok:
        print(f"VALIDATION FAILED for chunk {nn} — {len(errs)} error(s), nothing written:")
        for e in errs[:40]:
            print("  -", e)
        sys.exit(1)
    chunk = json.load(open(chunk_path(nn)))
    conf_dist = {"high": 0, "medium": 0, "low": 0}
    tag_hist = {}
    out = []
    for r in chunk["records"]:
        t = by_id[r["id"]]
        m = dict(r)
        m["categories"] = t.get("categories", [])
        m["confidence"] = t["confidence"]
        if t.get("reason"):
            m["tag_reason"] = t["reason"]
        out.append(m)
        conf_dist[t["confidence"]] += 1
        tag_hist[len(m["categories"])] = tag_hist.get(len(m["categories"]), 0) + 1
    os.makedirs(TAGDIR, exist_ok=True)
    json.dump({"chunk": int(nn), "count": len(out), "records": out},
              open(os.path.join(TAGDIR, f"chunk_{int(nn):02d}.json"), "w"),
              indent=1, ensure_ascii=False)
    man = load_manifest()
    man["chunks"][f"{int(nn):02d}"] = {
        "input_sha256": sha256(chunk_path(nn)),
        "count": len(out),
        "confidence": conf_dist,
        "tags_per_record": {str(k): tag_hist[k] for k in sorted(tag_hist)},
        "status": "done",
    }
    save_manifest(man)
    print(f"chunk {int(nn):02d} MERGED: {len(out)} records | confidence {conf_dist} | tags/record {dict(sorted(tag_hist.items()))}")

def cmd_check(nn):
    man = load_manifest()
    e = man["chunks"].get(f"{int(nn):02d}")
    if e and e.get("status") == "done" and os.path.exists(chunk_path(nn)) and e.get("input_sha256") == sha256(chunk_path(nn)):
        print(f"chunk {int(nn):02d}: done"); sys.exit(0)
    print(f"chunk {int(nn):02d}: pending"); sys.exit(1)

def cmd_status():
    man = load_manifest()
    allc = sorted(f for f in os.listdir(CHUNKDIR) if f.startswith("chunk_")) if os.path.isdir(CHUNKDIR) else []
    done = 0
    for f in allc:
        nn = f[6:8]
        e = man["chunks"].get(nn)
        if e and e.get("status") == "done":
            stale = e.get("input_sha256") != sha256(os.path.join(CHUNKDIR, f))
            print(f"  chunk_{nn}: DONE ({e['count']} recs){'  [STALE — input changed]' if stale else ''}")
            if not stale: done += 1
        else:
            print(f"  chunk_{nn}: pending")
    print(f"{done}/{len(allc)} chunks done")

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == "status": cmd_status()
    elif a[0] == "check": cmd_check(a[1])
    elif a[0] == "merge": cmd_merge(a[1], a[2])
    else: print("unknown command", a[0]); sys.exit(2)
