import re

from logfire import ScrubMatch
from opentelemetry.util.http import get_excluded_urls

from src.telemetry import _exclude_secret_urls_from_httpx_tracing, _scrub_callback, redact_url_secrets

TELEGRAM_URL = "https://api.telegram.org/bot123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw/sendMessage"
ETHERSCAN_URL = "https://api.etherscan.io/v2/api?chainid=1&module=gastracker&action=gasoracle&apikey=ABC123XYZ"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin?localization=false"


def test_redact_telegram_token():
    assert redact_url_secrets(TELEGRAM_URL) == "https://api.telegram.org/bot[REDACTED]/sendMessage"


def test_redact_apikey_keeps_other_params():
    assert redact_url_secrets(ETHERSCAN_URL) == (
        "https://api.etherscan.io/v2/api?chainid=1&module=gastracker&action=gasoracle&apikey=[REDACTED]"
    )


def test_redact_leaves_urls_without_secrets_untouched():
    assert redact_url_secrets(COINGECKO_URL) == COINGECKO_URL


def test_scrub_callback_keeps_url_readable():
    match = ScrubMatch(
        path=("attributes", "url"), value=ETHERSCAN_URL, pattern_match=re.search("apikey", ETHERSCAN_URL)
    )
    assert _scrub_callback(match) == redact_url_secrets(ETHERSCAN_URL)


def test_scrub_callback_falls_back_to_full_redaction():
    value = "my password is hunter2"
    match = ScrubMatch(path=("attributes", "note"), value=value, pattern_match=re.search("password", value))
    assert _scrub_callback(match) is None


def test_secret_urls_are_excluded_from_httpx_tracing(monkeypatch):
    monkeypatch.setenv("OTEL_PYTHON_HTTPX_EXCLUDED_URLS", "")
    monkeypatch.setenv("OTEL_PYTHON_EXCLUDED_URLS", "healthcheck")

    _exclude_secret_urls_from_httpx_tracing()
    excluded = get_excluded_urls("HTTPX")

    assert excluded.url_disabled(TELEGRAM_URL)
    assert excluded.url_disabled("https://api.telegram.org/file/bot123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw/a.jpg")
    assert excluded.url_disabled(ETHERSCAN_URL)
    assert excluded.url_disabled("http://hcpb-api:7777/healthcheck")
    assert not excluded.url_disabled(COINGECKO_URL)
    assert not excluded.url_disabled("http://hcpb-api:7777/calls")
