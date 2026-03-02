"""OpenTelemetry / Logfire configuration."""

import re

import logfire
from logfire import ScrubbingOptions, ScrubMatch

from src.config import settings as s


def _scrub_callback(match: ScrubMatch) -> str | None:
    """Redact API key values embedded in URLs (e.g. ?apikey=SECRET or Telegram bot tokens in path)."""
    if not isinstance(match.value, str):
        return None
    value = match.value
    changed = False
    if re.search(r"apikey=", value, re.IGNORECASE):
        value = re.sub(r"(?i)(apikey)=[^&\s#]+", r"\1=[REDACTED]", value)
        changed = True
    if re.search(r"/bot\d+:[A-Za-z0-9_-]+/", value):
        value = re.sub(r"/bot\d+:[A-Za-z0-9_-]+/", "/bot[REDACTED]/", value)
        changed = True
    return value if changed else None


def configure() -> None:
    """Configure Logfire and instrument httpx.

    Must be called before importing any handler modules so that all meters
    are registered on the real MeterProvider rather than the default no-op one.
    """
    logfire.configure(
        token=s.LOGFIRE_TOKEN.get_secret_value() if s.LOGFIRE_TOKEN else None,
        service_name=s.LOGFIRE_SERVICE_NAME,
        distributed_tracing=True,
        scrubbing=ScrubbingOptions(callback=_scrub_callback),
    )
    logfire.instrument_httpx()
