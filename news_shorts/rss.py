from typing import List, Dict
import feedparser
from . import config

Article = Dict[str, str]


def fetch_rss_feed(url: str, source: str, limit: int = 5) -> List[Article]:
    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:limit]
        arts: List[Article] = []
        for e in entries:
            arts.append({
                "source": source,
                "title": e.get("title", "").strip(),
                "summary": (e.get("summary") or e.get("description") or "").strip(),
                "link": e.get("link", "").strip(),
                "published": e.get("published", ""),
            })
        config.logger.info(f"    ✓ {len(arts)} from {source}")
        return arts
    except Exception as ex:
        config.logger.warning(f"    ✖ {source} failed: {ex}")
        return []


def fetch_all(limit_per_feed: int = config.FEED_LIMIT) -> List[Article]:
    config.logger.info("Step 1: Aggregating RSS feeds")
    all_arts: List[Article] = []
    seen = set()
    for src, url in config.RSS_SOURCES.items():
        for art in fetch_rss_feed(url, src, limit_per_feed):
            key = art["link"] or art["title"]
            if key and key not in seen:
                seen.add(key)
                all_arts.append(art)
    config.logger.info(f"Total unique articles fetched: {len(all_arts)}")
    config.logger.info("Sample articles:")
    for a in all_arts[:5]:
        config.logger.info(f" → [{a['source']}] {a['title']}")
    return all_arts

