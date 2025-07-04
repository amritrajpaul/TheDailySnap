import types
from news_shorts import script_gen

articles = [
    {"title": "T1", "summary": "S1", "source": "SRC"},
    {"title": "T2", "summary": "S2", "source": "SRC"},
]


def test_craft_script_json(monkeypatch):
    monkeypatch.setattr(script_gen, "_chat", lambda *a, **k: '{"segments": ["a", "b"]}')
    segs = script_gen.craft_script(articles)
    assert segs == ["a", "b"]


def test_craft_script_fallback(monkeypatch):
    monkeypatch.setattr(script_gen, "_chat", lambda *a, **k: 'One. Two.')
    segs = script_gen.craft_script(articles)
    assert segs == ["One.", "Two."]


def test_craft_daily_summary(monkeypatch):
    monkeypatch.setattr(script_gen, "_chat", lambda *a, **k: 'summary text')
    result = script_gen.craft_daily_summary(articles)
    assert result == 'summary text'
