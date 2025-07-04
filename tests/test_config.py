import importlib
import os
import types

import news_shorts.config as config


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("VIDEO_WIDTH", "800")
    monkeypatch.setenv("VIDEO_HEIGHT", "600")
    cfg = importlib.reload(config)
    assert cfg.VIDEO_SIZE == (800, 600)


def test_getenv_helpers(monkeypatch):
    monkeypatch.delenv("FOO", raising=False)
    assert config.getenv_int("FOO", 5) == 5
    monkeypatch.setenv("FOO", "notnum")
    assert config.getenv_int("FOO", 5) == 5
    monkeypatch.setenv("BAR", "")
    assert config.getenv_str("BAR", "baz") == "baz"


def test_with_retry(monkeypatch):
    calls = []

    def flaky(x):
        calls.append(x)
        if len(calls) < 3:
            raise ValueError("fail")
        return x * 2

    monkeypatch.setattr(config, "RETRY_LIMIT", 3)
    monkeypatch.setattr(config, "logger", types.SimpleNamespace(info=lambda *a, **k: None,
                                                                warning=lambda *a, **k: None,
                                                                error=lambda *a, **k: None))
    monkeypatch.setattr(config.time, "sleep", lambda x: None)
    result = config.with_retry(flaky, 5)
    assert result == 10
    assert len(calls) == 3

