#!/usr/bin/env python3
"""下载海报图片到本地 posters/ 目录"""

import json
import requests
import os
import time
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA = BASE / "data.json"
POSTERS_DIR = BASE / "posters"
POSTERS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://movie.douban.com/"
}

with open(DATA, "r", encoding="utf-8") as f:
    movies = json.load(f)

print(f"Total movies: {len(movies)}")

downloaded = 0
failed = 0
skipped = 0

for i, m in enumerate(movies):
    url = m.get("poster", "").strip()
    if not url:
        skipped += 1
        continue

    safe_name = re.sub(r'[\\/:*?"<>|]', "_", m["movieName"])
    local_path = POSTERS_DIR / f"{safe_name}.jpg"

    if local_path.exists() and local_path.stat().st_size > 1000:
        m["poster"] = f"posters/{safe_name}.jpg"
        downloaded += 1
        continue

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if resp.status_code == 200 and len(resp.content) > 500:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            m["poster"] = f"posters/{safe_name}.jpg"
            downloaded += 1
            print(f"  [{i+1}] OK: {m['movieName']} ({len(resp.content)//1024}KB)")
        else:
            failed += 1
            print(f"  [{i+1}] FAIL: {m['movieName']} (status={resp.status_code})")
    except Exception as e:
        failed += 1
        print(f"  [{i+1}] ERROR: {m['movieName']} - {e}")

    time.sleep(0.5)

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(movies, f, ensure_ascii=False, indent=2)

with open(BASE / "data.js", "w", encoding="utf-8") as f:
    f.write("const INLINE_DATA = " + json.dumps(movies, ensure_ascii=False, indent=2) + ";")

print(f"\nDone: {downloaded} downloaded, {failed} failed, {skipped} no URL")
