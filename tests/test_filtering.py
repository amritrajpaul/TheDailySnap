import types
from news_shorts import filtering

articles = [
    {"title": "A1", "summary": "S1", "source": "SRC"},
    {"title": "A2", "summary": "S2", "source": "SRC"},
    {"title": "A3", "summary": "S3", "source": "SRC"},
]

class DummyEmb:
    def __init__(self, emb):
        self.embedding = emb

def test_filter_stage1(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    data = [DummyEmb([1,1]), DummyEmb([1,1]), DummyEmb([0,1]), DummyEmb([-1,0])]
    monkeypatch.setattr(filtering.openai.embeddings, 'create', lambda **k: types.SimpleNamespace(data=data))
    result = filtering.filter_stage1(articles, top_k=2)
    assert [a['title'] for a in result] == ["A1", "A2"]


def test_filter_stage2(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    resp = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='[{"index": 2, "score": 9}, {"index": 0, "score": 8}]'))])
    monkeypatch.setattr(filtering.openai.chat.completions, 'create', lambda **k: resp)
    result = filtering.filter_stage2(articles, top_k=2)
    assert [a['title'] for a in result] == ["A3", "A1"]


def test_filter_stage2_bad_json(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    resp = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='oops'))])
    monkeypatch.setattr(filtering.openai.chat.completions, 'create', lambda **k: resp)
    result = filtering.filter_stage2(articles, top_k=2)
    assert [a['title'] for a in result] == ["A1", "A2"]
