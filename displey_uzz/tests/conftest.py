"""Testlar haqiqiy Telegram yoki Redis'ga ulanmaydi: baza o'rniga vaqtinchalik fayllar, bot o'rniga soxta obyekt."""
import importlib.util, os, sys, types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent

for k in ("UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN", "KV_REST_API_URL", "KV_REST_API_TOKEN", "WEB_APP_URL", "PUBLIC_URL"):
    os.environ.pop(k, None)
os.environ.update(BOT_TOKEN="123456:TEST", ADMIN_ID="777", WEBHOOK_SECRET="test-secret", VERCEL_ENV="production")


def _load():
    spec = importlib.util.spec_from_file_location("shop_api", ROOT / "api" / "index.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["shop_api"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def api_module():
    return _load()


@pytest.fixture
def api(api_module, tmp_path, monkeypatch):
    """Har bir test toza baza va soxta bot bilan boshlanadi."""
    monkeypatch.setattr(api_module, "_TMP", {k: str(tmp_path / f"{k}.json") for k in api_module._TMP})
    monkeypatch.setattr(api_module, "_catalog_version_ok", False)
    monkeypatch.setattr(api_module, "bot", MagicMock())
    return api_module


@pytest.fixture
def client(api):
    return api.app.test_client()


def make_message(data, chat_id=42, first_name="Ali", username="ali"):
    return types.SimpleNamespace(
        chat=types.SimpleNamespace(id=chat_id),
        from_user=types.SimpleNamespace(id=chat_id, first_name=first_name, last_name=None, username=username),
        web_app_data=types.SimpleNamespace(data=data),
    )
