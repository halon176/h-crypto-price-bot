"""OpenTelemetry / Logfire configuration."""

import os
import re

import logfire
from logfire import ScrubbingOptions, ScrubMatch

from src.config import settings as s

# Secrets carried inside URLs: the Telegram bot token in the path and `apikey=` query values.
_URL_SECRETS = re.compile(r"(?<=/bot)\d+:[A-Za-z0-9_-]+|(?<=apikey=)[^&\s#]+", re.IGNORECASE)

# Logfire never scrubs `url.full`, `http.url` or the span message, so an httpx span for one of these
# URLs would export the secret verbatim, to Logfire and to the console. Such requests are not traced.
# The OTel httpx instrumentation matches these regexes against the full URL with re.search.
_UNTRACED_URLS = (r"/bot\d+:", r"[?&]apikey=")


def redact_url_secrets(text: str) -> str:
    """Replace secrets embedded in URLs (Telegram bot token, apikey values) with [REDACTED]."""
    return _URL_SECRETS.sub("[REDACTED]", text)


def _scrub_callback(match: ScrubMatch) -> str | None:
    """Keep a value flagged by Logfire's scrubber readable when hiding its URL secrets is enough."""
    if not isinstance(match.value, str):
        return None
    redacted = redact_url_secrets(match.value)
    return redacted if redacted != match.value else None


def _exclude_secret_urls_from_httpx_tracing() -> None:
    """Add _UNTRACED_URLS to the OTel httpx exclusion list, keeping any value already configured."""
    configured = os.environ.get("OTEL_PYTHON_HTTPX_EXCLUDED_URLS") or os.environ.get("OTEL_PYTHON_EXCLUDED_URLS", "")
    os.environ["OTEL_PYTHON_HTTPX_EXCLUDED_URLS"] = ",".join(filter(None, [configured, *_UNTRACED_URLS]))


def configure() -> None:
    """Configure Logfire and instrument httpx.

    Must be called before importing any handler modules so that all meters
    are registered on the real MeterProvider rather than the default no-op one.
    """
    logfire.configure(
        token=s.LOGFIRE_TOKEN.get_secret_value() if s.LOGFIRE_TOKEN else None,
        # LOGFIRE_TOKEN is optional. Logfire's default (True) would otherwise prompt to pick a project
        # with the local CLI credentials, or block waiting for input when there is no terminal.
        send_to_logfire="if-token-present",
        service_name=s.LOGFIRE_SERVICE_NAME,
        distributed_tracing=True,
        scrubbing=ScrubbingOptions(callback=_scrub_callback),
    )
    # The instrumentation reads the exclusion list when it is installed.
    _exclude_secret_urls_from_httpx_tracing()
    logfire.instrument_httpx()
