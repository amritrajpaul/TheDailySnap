import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import importlib
import pytest
import news_shorts.config as config


@pytest.fixture
def fresh_config():
    """Reload config module after test to avoid cross-test state."""
    yield
    importlib.reload(config)
