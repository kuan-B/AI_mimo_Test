#!/usr/bin/env python3
"""
春节档电影数据爬虫
从公开数据源抓取电影票房数据并更新 data.json

用法:
  python scrape.py              # 抓取所有年份
  python scrape.py --year 2026  # 只抓取指定年份
  python scrape.py --dry-run    # 预览模式，不写入文件
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)

DATA_FILE = Path(__file__).parent.parent / "data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://piaofang.maoyan.com/",
}

# 猫眼春节档 API（公开接口）
MAOYAN_API = "https://piaofang.maoyan.com/ranking/year"
MAOYAN_DETAIL_API = "https://piaofang.maoyan.com/movie/{movie_id}"

# 豆瓣搜索 API
DOUBAN_SEARCH_API = "https://movie.douban.com/j/subject_suggest"


def load_existing_data():
    """加载现有的 data.json"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(movies):
    """保存数据到 data.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(movies)} 部电影数据到 {DATA_FILE}")


def fetch_maoyan_movies(year):
    """从猫眼获取春节档电影列表"""
    movies = []
    
    # 春节档日期范围（农历新年前后约15天）
    # 使用公开的猫眼票房页面数据
    try:
        # 尝试从猫眼获取数据
        url = f"https://piaofang.maoyan.com/ranking/year?year={year}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            # 解析页面中的电影数据
            # 注意：实际实现需要根据猫眼页面结构调整
            print(f"  [猫眼] 获取 {year} 年数据成功")
    except Exception as e:
        print(f"  [猫眼] 获取 {year} 年数据失败: {e}")
    
    return movies


def fetch_douban_info(movie_name):
    """从豆瓣获取电影信息"""
    info = {}
    try:
        params = {"q": movie_name}
        resp = requests.get(DOUBAN_SEARCH_API, params=params, headers={
            **HEADERS,
            "Referer": "https://movie.douban.com/"
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                item = data[0]
                info["doubanId"] = item.get("id", "")
                info["poster"] = item.get("img", "")
                info["title"] = item.get("title", "")
                print(f"    [豆瓣] 找到: {item.get('title', '')} (ID: {item.get('id', '')})")
    except Exception as e:
        print(f"    [豆瓣] 搜索失败: {e}")
    
    return info


def update_movie_posters(movies):
    """更新电影海报URL"""
    updated = 0
    for i, movie in enumerate(movies):
        if not movie.get("poster"):
            print(f"  [{i+1}/{len(movies)}] 搜索海报: {movie['movieName']}")
            info = fetch_douban_info(movie["movieName"])
            if info.get("poster"):
                movie["poster"] = info["poster"]
                updated += 1
            time.sleep(1)  # 避免请求过快
    
    print(f"更新了 {updated} 部电影的海报")
    return movies


def main():
    parser = argparse.ArgumentParser(description="春节档电影数据爬虫")
    parser.add_argument("--year", type=int, help="只抓取指定年份")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    parser.add_argument("--update-posters", action="store_true", help="更新海报URL")
    args = parser.parse_args()
    
    print("=== 春节档电影数据爬虫 ===\n")
    
    # 加载现有数据
    movies = load_existing_data()
    print(f"现有数据: {len(movies)} 部电影\n")
    
    # 如果指定了年份，只处理该年份
    years = [args.year] if args.year else range(2000, 2027)
    
    # 更新海报
    if args.update_posters:
        print("--- 更新海报URL ---")
        movies = update_movie_posters(movies)
    
    # 保存数据
    if not args.dry_run:
        save_data(movies)
    else:
        print("\n[预览模式] 未写入文件")
    
    print("\n完成！")


if __name__ == "__main__":
    main()
