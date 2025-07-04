import types
from news_shorts import rss
from news_shorts import config


class DummyFeed:
    def __init__(self, entries):
        self.entries = entries


def fake_parse(url):
    if '1' in url:
        return DummyFeed([
            {'title': 'T1', 'summary': 'S1', 'link': 'L1', 'published': 'now'},
            {'title': 'T2', 'summary': 'S2', 'link': 'L2', 'published': 'now'},
        ])
    else:
        return DummyFeed([
            {'title': 'T1', 'summary': 'S1', 'link': 'L1', 'published': 'now'},
        ])


def test_fetch_all_dedup(monkeypatch):
    monkeypatch.setattr(rss.feedparser, 'parse', fake_parse)
    monkeypatch.setitem(config.RSS_SOURCES, 'A', 'url1')
    monkeypatch.setitem(config.RSS_SOURCES, 'B', 'url2')
    arts = rss.fetch_all(limit_per_feed=5)
    assert len(arts) == 2
    links = {a['link'] for a in arts}
    assert links == {'L1', 'L2'}

