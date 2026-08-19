#!/usr/bin/env python3
"""Build a licensed 1,000-image inspiration gallery from Wikimedia Commons."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import threading
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "inspiration"
MANIFEST = ROOT / "data" / "inspiration.json"
PLAN_DIR = ROOT / "data" / "inspiration-plans"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "KoriKathaGallery/1.0 (houseofkorikatha@gmail.com)"
TARGET_PER_CATEGORY = 500
ALLOWED_LICENSES = {
    "CC0", "Public domain", "PDM", "CC BY 1.0", "CC BY 2.0", "CC BY 2.5",
    "CC BY 3.0", "CC BY 4.0", "CC BY-SA 1.0", "CC BY-SA 2.0",
    "CC BY-SA 2.5", "CC BY-SA 3.0", "CC BY-SA 4.0",
}
BLOCKED_TERMS = {
    "transparent sari", "low rise sari", "child", "children", "schoolgirl",
    "bikini", "lingerie", "nude", "nudity", "erotic", "porn", "corpse",
}
DOWNLOAD_LOCK = threading.Lock()
LAST_DOWNLOAD_START = 0.0

SEEDS = {
    "saree": [
        "Category:Saris", "Category:Saris from India", "Category:Sari fabric",
        "Category:Jamdani", "Category:Tant sari", "Category:Baluchori saree",
        "Category:Saris by color", "Category:Sari shops in India",
        "Category:Wedding saris", "Category:Saris of West Bengal",
    ],
    "jewellery": [
        "Category:Jewellery of India", "Category:Jewellery in India by type",
        "Category:Gold jewellery of India", "Category:Silver jewellery of India",
        "Category:Jhumka (earring style)", "Category:Bangles",
        "Category:Necklaces of India", "Category:Earrings in India",
        "Category:Mughal jewellery", "Category:Wedding necklaces",
    ],
}

SEARCHES = {
    "saree": [
        "Indian saree", "sari fabric", "Bengali saree", "Jamdani", "Tant sari",
        "Baluchari saree", "silk saree", "cotton saree", "saree shop India",
        "sari textile museum", "sari border", "sari weaving",
    ],
    "jewellery": [
        "Indian jewellery", "Indian necklace", "Indian earrings", "Indian bangles",
        "jhumka", "gold jewellery India", "silver jewellery India", "Mughal jewellery",
        "Indian pendant", "Indian jewelry museum", "Bengal jewellery", "Indian anklet",
    ],
}


def api(params: dict) -> dict:
    query = {"format": "json", "formatversion": "2", "origin": "*", **params}
    request = urllib.request.Request(
        API + "?" + urllib.parse.urlencode(query), headers={"User-Agent": USER_AGENT}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def blocked(value: str) -> bool:
    lowered = value.casefold()
    return any(term in lowered for term in BLOCKED_TERMS)


def category_files(seeds: list[str], maximum: int = 2500) -> list[str]:
    queue = [(seed, 0) for seed in seeds]
    visited: set[str] = set()
    files: dict[str, None] = {}
    while queue and len(files) < maximum:
        category, depth = queue.pop(0)
        if category in visited or blocked(category):
            continue
        visited.add(category)
        continuation = None
        while True:
            params = {
                "action": "query", "list": "categorymembers", "cmtitle": category,
                "cmtype": "file|subcat", "cmlimit": "500",
            }
            if continuation:
                params["cmcontinue"] = continuation
            data = api(params)
            for member in data.get("query", {}).get("categorymembers", []):
                title = member["title"]
                if blocked(title):
                    continue
                if member["ns"] == 6 and title.lower().endswith((".jpg", ".jpeg")):
                    files[title] = None
                elif member["ns"] == 14 and depth < 3:
                    queue.append((title, depth + 1))
            continuation = data.get("continue", {}).get("cmcontinue")
            if not continuation or len(files) >= maximum:
                break
    return list(files)


def search_files(queries: list[str], maximum: int = 2500) -> list[str]:
    files: dict[str, None] = {}
    for query in queries:
        continuation = None
        for _ in range(10):
            params = {
                "action": "query", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
                "gsrnamespace": "6", "gsrlimit": "50", "prop": "info",
            }
            if continuation:
                params["gsrcontinue"] = continuation
            data = api(params)
            for page in data.get("query", {}).get("pages", []):
                title = page["title"]
                if title.lower().endswith((".jpg", ".jpeg")) and not blocked(title):
                    files[title] = None
            continuation = data.get("continue", {}).get("gsrcontinue")
            if not continuation or len(files) >= maximum:
                break
        if len(files) >= maximum:
            break
    return list(files)


def clean_markup(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def details(titles: list[str], category: str) -> list[dict]:
    accepted = []
    for start in range(0, len(titles), 50):
        data = api({
            "action": "query", "titles": "|".join(titles[start:start + 50]),
            "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": "640",
        })
        for page in data.get("query", {}).get("pages", []):
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata", {})
            license_name = clean_markup(meta.get("LicenseShortName", {}).get("value", ""))
            if info.get("mime") != "image/jpeg" or license_name not in ALLOWED_LICENSES:
                continue
            title = page.get("title", "")
            description = clean_markup(meta.get("ImageDescription", {}).get("value", ""))
            if blocked(title + " " + description):
                continue
            accepted.append({
                "title": title.removeprefix("File:").rsplit(".", 1)[0],
                "category": category,
                "author": clean_markup(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons contributor",
                "license": license_name,
                "license_url": meta.get("LicenseUrl", {}).get("value", "https://commons.wikimedia.org/wiki/Commons:Licensing"),
                "source": info.get("descriptionurl"),
                "download": info.get("thumburl") or info.get("url"),
                "width": info.get("thumbwidth") or info.get("width"),
                "height": info.get("thumbheight") or info.get("height"),
            })
        if len(accepted) >= TARGET_PER_CATEGORY:
            break
    return accepted[:TARGET_PER_CATEGORY]


def fetch_one(item: dict, number: int) -> dict:
    global LAST_DOWNLOAD_START
    category = item["category"]
    relative = f"assets/inspiration/{category}/{category}-{number:04d}.jpg"
    destination = ROOT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        request = urllib.request.Request(item["download"], headers={"User-Agent": USER_AGENT})
        for attempt in range(8):
            try:
                with DOWNLOAD_LOCK:
                    delay = 0.55 - (time.monotonic() - LAST_DOWNLOAD_START)
                    if delay > 0:
                        time.sleep(delay)
                    LAST_DOWNLOAD_START = time.monotonic()
                with urllib.request.urlopen(request, timeout=60) as response:
                    destination.write_bytes(response.read())
                break
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    time.sleep(int(error.headers.get("Retry-After", "30")))
                    continue
                if attempt == 7:
                    raise
                time.sleep(2 * (attempt + 1))
            except Exception:
                if attempt == 7:
                    raise
                time.sleep(2 * (attempt + 1))
    result = {key: value for key, value in item.items() if key != "download"}
    result.update({"id": f"{category}-{number:04d}", "image": relative})
    return result


def collect(category: str, download: bool = False) -> list[dict]:
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    plan_file = PLAN_DIR / f"{category}.json"
    if plan_file.exists():
        items = json.loads(plan_file.read_text(encoding="utf-8"))
        print(f"{category}: resumed saved {len(items)}-image plan", flush=True)
    else:
        candidates = category_files(SEEDS[category])
        for title in search_files(SEARCHES[category]):
            if title not in candidates:
                candidates.append(title)
        print(f"{category}: checking {len(candidates)} candidate files", flush=True)
        items = details(candidates, category)
        if len(items) < TARGET_PER_CATEGORY:
            raise RuntimeError(f"Only {len(items)} licensed {category} images found")
        plan_file.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if download:
        completed = []
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(fetch_one, item, index): index for index, item in enumerate(items, 1)}
            for future in as_completed(futures):
                completed.append(future.result())
                if len(completed) % 50 == 0:
                    print(f"{category}: downloaded {len(completed)}/{TARGET_PER_CATEGORY}", flush=True)
        return sorted(completed, key=lambda item: item["id"])

    completed = []
    for index, item in enumerate(items, 1):
        relative = f"assets/inspiration/{category}/{category}-{index:04d}.jpg"
        local_file = ROOT / relative
        result = {key: value for key, value in item.items() if key != "download"}
        result.update({
            "id": f"{category}-{index:04d}",
            "image": relative if local_file.exists() else item["download"],
        })
        completed.append(result)
    return completed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Mirror every image locally")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sarees = collect("saree", args.download)
    jewellery = collect("jewellery", args.download)
    all_items = [item for pair in zip(sarees, jewellery) for item in pair]
    assert len(all_items) == 1000
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(all_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    local_items = [item for item in all_items if not item["image"].startswith("http")]
    total_bytes = sum((ROOT / item["image"]).stat().st_size for item in local_items)
    print(f"Created {len(all_items)}-image gallery; {len(local_items)} locally mirrored ({total_bytes / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
