import asyncio
from types import SimpleNamespace

import pytest

from src.handlers import cmc_calls

UPDATE = SimpleNamespace(effective_chat=SimpleNamespace(id=1), effective_user=SimpleNamespace(id=2))


@pytest.fixture
def errors(monkeypatch):
    sent = []

    async def fake_send_error(e_type, update, context):
        sent.append(e_type)

    monkeypatch.setattr(cmc_calls, "send_error", fake_send_error)
    return sent


def test_cmc_without_symbol_asks_for_one(errors):
    asyncio.run(cmc_calls.cmc_price_handler(UPDATE, SimpleNamespace(args=[])))

    assert errors == ["symbol"]


def test_cmc_id_without_coin_list(monkeypatch):
    monkeypatch.setattr(cmc_calls.cmc_coin_list, "coin_list", None)

    assert asyncio.run(cmc_calls.get_cmc_id("btc")) == []


def test_cmc_key_info_reports_failed_request(monkeypatch, errors):
    async def fake_fetch_url(url, headers=None, service="unknown", timeout=30.0):
        return None

    monkeypatch.setattr(cmc_calls, "fetch_url", fake_fetch_url)

    asyncio.run(cmc_calls.cmc_key_info(UPDATE, None))

    assert errors == ["generic"]
