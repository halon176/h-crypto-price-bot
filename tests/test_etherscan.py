import asyncio
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from src.handlers import ethersca_calls

# Real Etherscan V2 payloads (Ethereum mainnet, 2026-10-28), trimmed.
GAS_ORACLE = {
    "status": "1",
    "message": "OK",
    "result": {"SafeGasPrice": "0.095947658", "FastGasPrice": "0.105542539", "suggestBaseFee": "0.095947658"},
}
ETH_PRICE = {"status": "1", "message": "OK", "result": {"ethbtc": "0.02898854", "ethusd": "2353.96"}}
UPDATE = SimpleNamespace(effective_chat=SimpleNamespace(id=1), effective_user=SimpleNamespace(id=2))


@pytest.fixture
def fetched_urls(monkeypatch):
    """Replace fetch_url with a stub answering with `response`; collect the requested URLs."""
    urls = []

    def install(response):
        async def fake_fetch_url(url, headers=None, service="unknown", timeout=30.0):
            urls.append(url)
            return response

        monkeypatch.setattr(ethersca_calls, "fetch_url", fake_fetch_url)
        return urls

    monkeypatch.setattr(ethersca_calls.s, "ETHSCAN_API_KEY", SecretStr("KEY"))
    return install


def test_etherscan_result_calls_v2_on_mainnet(fetched_urls):
    urls = fetched_urls({"status": "1", "message": "OK", "result": {"ethusd": "2353.96"}})

    assert asyncio.run(ethersca_calls._etherscan_result("stats", "ethprice")) == {"ethusd": "2353.96"}
    assert urls == ["https://api.etherscan.io/v2/api?chainid=1&module=stats&action=ethprice&apikey=KEY"]


@pytest.mark.parametrize(
    "response",
    [
        {"status": "0", "message": "NOTOK", "result": "Invalid API Key (#err2)|etherscan"},
        None,
    ],
)
def test_etherscan_result_is_none_on_failure(fetched_urls, response):
    fetched_urls(response)

    assert asyncio.run(ethersca_calls._etherscan_result("gastracker", "gasoracle")) is None


@pytest.fixture
def replies(monkeypatch):
    """Capture what gas_handler sends back: ("text", message) or ("error", error type)."""
    sent = []

    async def fake_send_tg(ctx, chat_id, text=None, **kwargs):
        sent.append(("text", text))

    async def fake_send_error(e_type, update, context):
        sent.append(("error", e_type))

    monkeypatch.setattr(ethersca_calls, "send_tg", fake_send_tg)
    monkeypatch.setattr(ethersca_calls, "send_error", fake_send_error)
    monkeypatch.setattr(ethersca_calls.s, "ETHSCAN_API_KEY", SecretStr("KEY"))
    return sent


def test_gas_handler_shows_sub_gwei_prices(monkeypatch, replies):
    async def fake_fetch_url(url, headers=None, service="unknown", timeout=30.0):
        return GAS_ORACLE if "action=gasoracle" in url else ETH_PRICE

    monkeypatch.setattr(ethersca_calls, "fetch_url", fake_fetch_url)

    asyncio.run(ethersca_calls.gas_handler(UPDATE, None))

    [(kind, message)] = replies
    assert kind == "text"
    lines = message.splitlines()
    assert lines[3].split() == ["😎", "Safe", "0.0959", "0.00474$"]
    assert lines[4].split() == ["😎", "Fast", "0.106", "0.00522$"]
    assert lines[5].split() == ["😎", "Suggested", "0.0959", "0.00474$"]


def test_gas_handler_reports_etherscan_errors(monkeypatch, replies):
    async def fake_fetch_url(url, headers=None, service="unknown", timeout=30.0):
        return {"status": "0", "message": "NOTOK", "result": "Max calls per sec rate limit reached (3/sec)"}

    monkeypatch.setattr(ethersca_calls, "fetch_url", fake_fetch_url)

    asyncio.run(ethersca_calls.gas_handler(UPDATE, None))

    assert replies == [("error", "generic")]
