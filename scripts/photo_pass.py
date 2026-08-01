#!/usr/bin/env python3
"""
photo_pass.py — Batched MediaWiki-API photo pass across all MOH recipients lacking photo_url.
Processes in priority order: post-2014 top-up first, then modern-to-ancient by conflict era.
Commits + pushes after each batch of ~250. Cache-fingerprinted — safe to interrupt and resume.
Usage: python3 scripts/photo_pass.py
"""

import json
import os
import re
import sys
import time
import subprocess
import threading
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES_FILE = ROOT / "data" / "stories.json"
CACHE_FILE = ROOT / "data" / "photo_cache.json"

BATCH_SIZE = 250
MAX_WORKERS = 2
USER_AGENT = (
    "MOHStoriesBrowser/1.0 (https://everymedal.org; "
    "historical-research; contact: claimtheacre@gmail.com)"
)
API_BASE = "https://en.wikipedia.org/w/api.php"

# Top-up record IDs — processed first (modern, high photo availability)
TOPUP_IDS = {
    "william-shemin", "henry-johnson-wwi", "florent-groberg", "edward-c-byers",
    "charles-kettles", "james-c-mccloughan", "gary-m-rose", "britt-slabinski",
    "garlin-m-conner", "john-a-chapman", "ronald-j-shurer", "john-l-canley",
    "travis-w-atkins", "david-g-bellavia", "matthew-o-williams", "thomas-p-payne",
    "ralph-puckett", "alwyn-c-cashe", "christopher-a-celiz", "earl-d-plumlee",
    "dwight-w-birdwell", "john-j-duffy", "dennis-m-fujii", "edward-n-kaneshiro",
    "paris-d-davis", "larry-l-taylor", "philip-g-shadrach", "george-d-wilson",
    "kenneth-j-david", "eric-slover", "james-capers-jr", "john-w-ripley",
    "terry-p-richardson", "fred-w-zabitosky", "gerald-o-young", "marvin-r-young",
}

# Era priority: higher = processed earlier (modern recipients have better photo coverage)
CONFLICT_PRIORITY = {
    "Venezuela Intervention (2026)": 100,
    "War on Terrorism (Afghanistan)": 95,
    "War on Terrorism (Iraq)": 90,
    "Somalia (Operation Restore Hope)": 85,
    "Vietnam War": 80,
    "Korean War": 75,
    "World War II": 70,
    "World War I": 60,
    "Mexican Campaign (Vera Cruz)": 50,
    "Spanish-American War": 40,
    "Philippine-American War": 35,
    "China Relief Expedition (Boxer Rebellion)": 30,
    "Nicaraguan Campaign": 25,
    "Haitian Campaign": 25,
    "Dominican Campaign": 25,
    "Interim Awards (Peacetime)": 15,
    "Indian Campaigns": 10,
    "U.S. Civil War": 5,
    "Unknown": 1,
}

# Filename patterns that indicate NOT a portrait
NON_PORTRAIT_RE = re.compile(
    r"(?:grave|tomb|memorial|mausoleum|cemet|burial|"
    r"\bship\b|_uss_|\buss\b|destroyer|cruiser|carrier|submarine|frigate|gunboat|sloop|"
    r"monument|statue|plaque|marker|obelisk|bas[_-]relief|"
    r"building|barracks|airfield|air_base|air_station|fort_[a-z]|_camp_|hangar|"
    r"painting|drawing|sketch|engraving|lithograph|illustration|artwork|"
    r"coin|stamp|ribbon|award_ribbon|"
    r"landscape|terrain|aerial|battlefield_view|"
    r"\bflag\b|colors|banner)",
    re.IGNORECASE,
)

# ---- Global rate limiter (shared across all worker threads) ----
_last_req_time = [0.0]
_rate_lock = threading.Lock()
MIN_INTERVAL = 0.6  # ~1.7 req/s max across all workers (conservative, avoids 429)
_429_backoff = 30   # seconds to sleep on 429 before retry


def _query(params: dict, retry: bool = True) -> dict:
    """Rate-limited MediaWiki API call with one retry on 429."""
    with _rate_lock:
        now = time.monotonic()
        gap = MIN_INTERVAL - (now - _last_req_time[0])
        if gap > 0:
            time.sleep(gap)
        _last_req_time[0] = time.monotonic()

    params["format"] = "json"
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429 and retry:
            print(f"  [429] rate limited — sleeping {_429_backoff}s then retrying…",
                  file=sys.stderr, flush=True)
            time.sleep(_429_backoff)
            return _query(params, retry=False)  # one retry only
        raise


def name_to_first_last(name_field: str) -> str:
    """'Last, First M.' → 'First M. Last'"""
    if "," in name_field:
        parts = name_field.split(",", 1)
        return f"{parts[1].strip()} {parts[0].strip()}"
    return name_field.strip()


def extract_filename(image_url: str) -> str | None:
    """Pull the Commons filename from an upload.wikimedia.org URL."""
    m = re.search(
        r"/commons(?:/thumb)?/[0-9a-f]/[0-9a-f]{2}/([^/]+?)(?:/\d+px-.*)?$",
        image_url,
    )
    return urllib.parse.unquote(m.group(1)) if m else None


def is_acceptable_license(meta: dict) -> bool:
    short = meta.get("LicenseShortName", {}).get("value", "")
    lic_url = meta.get("LicenseUrl", {}).get("value", "")
    sl = short.lower()

    if any(x in sl for x in ("pd", "public domain", "cc0", "no restrictions")):
        return True
    if re.search(
        r"u\.?s\.?\s*(government|army|navy|marine|air force|coast guard|federal)", sl
    ):
        return True
    # CC BY or CC BY-SA (any version), reject NC/ND
    if re.match(r"cc[\s-]*by(?:[\s-]+sa)?(?:\s+\d)?(?:\.\d)?$", sl.strip()):
        return "nc" not in sl and "nd" not in sl
    if "creativecommons.org/licenses/by" in lic_url:
        return "nc" not in lic_url and "nd" not in lic_url
    if "creativecommons.org/publicdomain" in lic_url:
        return True
    return False


def build_credit(meta: dict) -> str:
    short = meta.get("LicenseShortName", {}).get("value", "")
    artist_html = meta.get("Artist", {}).get("value", "")
    artist = re.sub(r"<[^>]+>", "", artist_html).strip()[:120]

    sl = short.lower()
    is_pd = any(
        x in sl
        for x in (
            "pd", "public domain", "cc0", "government", "us army", "us navy",
            "usmc", "u.s. marine", "air force", "coast guard", "federal",
            "no restrictions",
        )
    )
    if is_pd or not short:
        return "Wikimedia Commons — public domain"
    if artist:
        return f"{artist} / Wikimedia Commons — {short}"
    return f"Wikimedia Commons — {short}"


def fetch_photo(record: dict) -> tuple[str, str | None, str | None]:
    """
    Returns (id, photo_url, photo_credit) or (id, None, None).
    Queries Wikipedia: search → lead image → non-portrait filter → license → 500px thumb.
    """
    rid = record["id"]
    name = record.get("name", "")
    search_name = name_to_first_last(name)
    last_name = name.split(",")[0].strip().lower() if "," in name else name.lower()

    try:
        # Step 1: Search Wikipedia for the recipient's article
        res = _query({
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{search_name} Medal of Honor",
            "gsrlimit": 3,
            "prop": "pageimages",
            "piprop": "original",
        })
        pages = res.get("query", {}).get("pages", {})
        if not pages:
            return (rid, None, None)

        # Prefer a hit whose title contains the last name; fall back to top result
        best = None
        for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            if last_name in p.get("title", "").lower():
                best = p
                break
        if best is None:
            best = min(pages.values(), key=lambda p: p.get("index", 99))

        image_url = best.get("original", {}).get("source", "")
        if not image_url:
            return (rid, None, None)

        # Step 2: Extract filename
        filename = extract_filename(image_url)
        if not filename:
            return (rid, None, None)

        # Step 3: Reject obvious non-portraits by filename
        if NON_PORTRAIT_RE.search(filename):
            return (rid, None, None)

        # Step 4: Get imageinfo — license + 500px thumb
        info = _query({
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "extmetadata|url",
            "iiurlwidth": 500,
        })
        ipages = info.get("query", {}).get("pages", {})
        if not ipages:
            return (rid, None, None)

        ipage = next(iter(ipages.values()))
        imageinfo = (ipage.get("imageinfo") or [{}])[0]
        meta = imageinfo.get("extmetadata", {})
        thumburl = imageinfo.get("thumburl", "")

        if not thumburl or not is_acceptable_license(meta):
            return (rid, None, None)

        return (rid, thumburl, build_credit(meta))

    except Exception as exc:
        print(f"  WARN {rid}: {exc}", file=sys.stderr, flush=True)
        return (rid, None, None)


def git_commit_push(batch_num: int, found: int, total: int):
    pct = round(found / total * 100) if total else 0
    msg = f"photos batch {batch_num:02d}: {found} found of {total} processed ({pct}%)"
    subprocess.run(
        ["git", "add", "data/stories.json", "data/photo_cache.json"],
        cwd=ROOT, check=True, capture_output=True,
    )
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT
    )
    if diff.returncode == 0:
        print(f"  [batch {batch_num:02d}] no staged changes — skipping commit")
        return
    subprocess.run(
        ["git", "commit", "-m", msg], cwd=ROOT, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "push", "origin", "main"], cwd=ROOT, check=True, capture_output=True
    )
    print(f"  [batch {batch_num:02d}] committed + pushed: {msg}", flush=True)


def priority_key(record: dict) -> int:
    rid = record["id"]
    if rid in TOPUP_IDS:
        return 10_000_000  # first batch
    conf = record.get("conflict") or ""
    base = CONFLICT_PRIORITY.get(conf, 1)
    year = record.get("year") or 0
    return base * 10_000 + year


def print_stats(stories: list):
    print("\n--- Coverage by conflict (photos found / total) ---")
    by_conf: dict[str, dict] = {}
    for r in stories:
        c = r.get("conflict") or "Unknown"
        if c not in by_conf:
            by_conf[c] = {"total": 0, "found": 0}
        by_conf[c]["total"] += 1
        if r.get("photo_url"):
            by_conf[c]["found"] += 1

    rows = sorted(by_conf.items(), key=lambda x: -x[1]["total"])
    grand_t = grand_f = 0
    for c, s in rows:
        grand_t += s["total"]
        grand_f += s["found"]
        pct = s["found"] / s["total"] * 100 if s["total"] else 0
        print(f"  {c:<48} {s['found']:>4}/{s['total']:<6} {pct:>5.1f}%")
    overall = grand_f / grand_t * 100 if grand_t else 0
    print(f"  {'TOTAL':<48} {grand_f:>4}/{grand_t:<6} {overall:>5.1f}%")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MediaWiki photo pass for MOH recipients")
    parser.add_argument("--start-batch", type=int, default=None,
                        help="Override starting batch number (for sequential commit messages)")
    args = parser.parse_args()

    print(f"Loading {STORIES_FILE.name}…", flush=True)
    stories: list[dict] = json.loads(STORIES_FILE.read_text())

    cache: dict = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())

    already_photo = sum(1 for r in stories if r.get("photo_url"))
    todo = [r for r in stories if not r.get("photo_url") and r["id"] not in cache]

    print(
        f"  {len(stories)} total | {already_photo} have photos | "
        f"{len(cache)} cached | {len(todo)} to process",
        flush=True,
    )

    if not todo:
        print("Nothing new to process.")
        print_stats(stories)
        return

    todo.sort(key=priority_key, reverse=True)
    lookup = {r["id"]: r for r in stories}

    # Resume batch numbering
    if args.start_batch is not None:
        batch_num = args.start_batch - 1  # increments to start_batch on first iteration
    else:
        batch_num = len(cache) // BATCH_SIZE
    session_found = 0

    idx = 0
    while idx < len(todo):
        batch = todo[idx : idx + BATCH_SIZE]
        idx += BATCH_SIZE
        batch_num += 1
        batch_found = 0

        print(f"\n=== Batch {batch_num:02d} — {len(batch)} records ===", flush=True)
        t0 = time.monotonic()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(fetch_photo, rec): rec["id"] for rec in batch}
            done_count = 0
            for fut in as_completed(futures):
                rid, url, credit = fut.result()
                done_count += 1
                cache[rid] = {
                    "photo_url": url,
                    "photo_credit": credit,
                    "processed": True,
                }
                if url:
                    lookup[rid]["photo_url"] = url
                    lookup[rid]["photo_credit"] = credit
                    batch_found += 1
                    session_found += 1
                    print(f"  + {rid}", flush=True)
                if done_count % 50 == 0:
                    elapsed = time.monotonic() - t0
                    print(
                        f"  … {done_count}/{len(batch)} done  "
                        f"({batch_found} found, {elapsed:.0f}s elapsed)",
                        flush=True,
                    )

        elapsed = time.monotonic() - t0
        print(
            f"  Batch {batch_num:02d} complete: {batch_found}/{len(batch)} found "
            f"in {elapsed:.0f}s",
            flush=True,
        )

        STORIES_FILE.write_text(json.dumps(stories, ensure_ascii=False))
        CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
        git_commit_push(batch_num, batch_found, len(batch))

    total_with_photo = sum(1 for r in stories if r.get("photo_url"))
    print(
        f"\n=== PASS COMPLETE ===\n"
        f"  Session: {session_found} new photos found across {len(todo)} records\n"
        f"  Total photos in corpus: {total_with_photo}/{len(stories)}"
    )
    print_stats(stories)


if __name__ == "__main__":
    main()
