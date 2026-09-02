#!/usr/bin/env python3
"""
xhs-batch-search.py - XHS 多关键词批量搜索工具
Usage:
  python xhs-batch-search.py "keyword1" "keyword2" ... [--limit N]
  python xhs-batch-search.py --file keywords.txt [--limit N]
"""
import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

from cn_scraper_mcp.engines.xiaohongshu import XiaohongshuEngine


def search_one(engine, keyword, limit=10):
    """Run one XHS search and return structured data."""
    result = engine.search(keyword, limit=limit)
    items = []
    for it in result.get("items", []):
        items.append({
            "title": it.get("title", ""),
            "author": it.get("author", ""),
            "likes": it.get("likes", ""),
            "noteId": it.get("noteId", ""),
            "xsec_token": it.get("xsec_token", ""),
            "href": it.get("href", ""),
            "url": "https://www.xiaohongshu.com" + it.get("href", ""),
        })
    return {
        "keyword": keyword,
        "state": result.get("state"),
        "count": result.get("count"),
        "items": items,
        "error_code": result.get("error_code"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("keywords", nargs="*", help="Search keywords")
    parser.add_argument("--file", help="Read keywords from file (one per line)")
    parser.add_argument("--limit", type=int, default=10, help="Items per keyword")
    parser.add_argument("--out", help="Output JSON file path")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between searches (s)")
    args = parser.parse_args()

    keywords = list(args.keywords)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            keywords.extend([line.strip() for line in f if line.strip()])

    if not keywords:
        print("Usage: xhs-batch-search.py <keyword> [<keyword>...] [--limit N]")
        sys.exit(1)

    engine = XiaohongshuEngine()
    out = {
        "queries": [{"keyword": k, "limit": args.limit} for k in keywords],
        "results": [],
        "ts": time.time(),
        "iso": datetime.now().isoformat(),
    }

    for i, kw in enumerate(keywords):
        print(f"[{i+1}/{len(keywords)}] Searching: {kw} (limit={args.limit})")
        try:
            r = search_one(engine, kw, args.limit)
            out["results"].append(r)
            print(f"   Found: {r['count']} items | state={r['state']}")
            for j, item in enumerate(r["items"][:3]):
                print(f"     {j+1}. {item['title'][:50]} | by {item['author']} | likes={item['likes']}")
        except Exception as e:
            print(f"   ERROR: {e}")
            out["results"].append({"keyword": kw, "error": str(e), "items": []})
        if i < len(keywords) - 1:
            time.sleep(args.delay)

    out_path = args.out or f"xhs-batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out_path = Path(out_path)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(r.get("count", 0) for r in out["results"])
    print(f"\nSaved to: {out_path}")
    print(f"Total items: {total} across {len(keywords)} keywords")


if __name__ == "__main__":
    main()
