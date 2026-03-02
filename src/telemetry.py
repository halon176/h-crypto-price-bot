"""OpenTelemetry / Logfire configuration."""

import re

import logfire
from logfire import ScrubbingOptions, ScrubMatch

from src.config import settings as s


def _scrub_callback(match: ScrubMatch) -> str | None:
    """Redact API key values embedded in URLs (e.g. ?apikey=SECRET)."""
    if isinstance(match.value, str) and re.search(r"apikey=", match.value, re.IGNORECASE):
        return re.sub(r"(?i)(apikey)=[^&\s#]+", r"\1=[REDACTED]", match.value)
    return None


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
