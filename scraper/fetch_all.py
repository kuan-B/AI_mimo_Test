#!/usr/bin/env python3
"""批量从豆瓣获取海报URL和电影简介"""

import json
import requests
import os
import time
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).parent.parent
DATA = BASE / "data.json"
POSTERS_DIR = BASE / "posters"
POSTERS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

SEARCH_API = "https://movie.douban.com/j/subject_suggest"
MOVIE_PAGE = "https://movie.douban.com/subject/{id}/"

with open(DATA, "r", encoding="utf-8") as f:
    movies = json.load(f)

needs = [(i, m) for i, m in enumerate(movies) if not m.get("poster", "").strip() or not m.get("synopsis", "").strip()]
print(f"Need update: {len(needs)} movies")

def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', "_", name)

def search_douban(query):
    try:
        resp = requests.get(SEARCH_API, params={"q": query}, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://movie.douban.com/",
            "Accept": "application/json",
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data[0]
    except Exception as e:
        print(f"    Search error: {e}")
    return None

def get_movie_page(douban_id):
    """Fetch movie page and extract synopsis"""
    try:
        url = MOVIE_PAGE.format(id=douban_id)
        resp = requests.get(url, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "text/html",
        }, timeout=15)
        if resp.status_code == 200:
            html = resp.text
            # Try to extract synopsis from meta description
            match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
            if match:
                desc = match.group(1).strip()
                # Clean up the description
                desc = re.sub(r'\s*--\s*豆瓣.*$', '', desc)
                desc = re.sub(r'\(豆瓣\)', '', desc).strip()
                if len(desc) > 10:
                    return desc
            # Try alternative: look for the synopsis div
            match = re.search(r'<span property="v:summary"[^>]*>(.*?)</span>', html, re.DOTALL)
            if match:
                desc = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if len(desc) > 10:
                    return desc
    except Exception as e:
        print(f"    Page error: {e}")
    return ""

def download_image(url, filepath):
    try:
        resp = requests.get(url, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://movie.douban.com/",
        }, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 2000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False

updated = 0
for idx, (i, m) in enumerate(needs):
    name = m["movieName"]
    year = m.get("year", "")
    has_poster = bool(m.get("poster", "").strip())
    has_synopsis = bool(m.get("synopsis", "").strip())

    print(f"[{idx+1}/{len(needs)}] {name}")

    # Search Douban
    queries = [name, f"{name} {year}"]
    info = None
    for q in queries:
        info = search_douban(q)
        if info:
            break
        time.sleep(1)

    if not info:
        print(f"  NOT FOUND on Douban")
        time.sleep(1)
        continue

    douban_id = info.get("id", "")
    douban_title = info.get("title", "")
    img_url = info.get("img", "")

    print(f"  Douban: {douban_title} (ID: {douban_id})")

    changed = False

    # Download poster if needed
    if not has_poster and img_url:
        fname = safe_name(name) + ".jpg"
        filepath = POSTERS_DIR / fname
        if download_image(img_url, filepath):
            m["poster"] = f"posters/{fname}"
            print(f"  Poster: OK ({os.path.getsize(filepath)//1024}KB)")
            changed = True
        else:
            print(f"  Poster: FAIL")
        time.sleep(0.5)

    # Get synopsis if needed
    if not has_synopsis and douban_id:
        synopsis = get_movie_page(douban_id)
        if synopsis:
            m["synopsis"] = synopsis
            print(f"  Synopsis: {synopsis[:50]}...")
            changed = True
        else:
            print(f"  Synopsis: EMPTY")
        time.sleep(1)

    if changed:
        updated += 1

    time.sleep(1.5)  # Rate limit between movies

# Save
with open(DATA, "w", encoding="utf-8") as f:
    json.dump(movies, f, ensure_ascii=False, indent=2)

# Regenerate data.js
with open(BASE / "data.js", "w", encoding="utf-8") as f:
    f.write("const INLINE_DATA = " + json.dumps(movies, ensure_ascii=False, indent=2) + ";")

poster_total = sum(1 for m in movies if m.get("poster", "").strip())
synopsis_total = sum(1 for m in movies if m.get("synopsis", "").strip())
print(f"\nDone: {updated} updated")
print(f"Posters: {poster_total}/{len(movies)}")
print(f"Synopses: {synopsis_total}/{len(movies)}")
