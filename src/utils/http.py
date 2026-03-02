import logging
from time import perf_counter

import httpx
import logfire
from opentelemetry import metrics as otel_metrics
from opentelemetry import trace as otel_trace

from src.config import settings as s

api_headers = {"X-API-KEY": s.hcpb_api_key.get_secret_value()} if s.hcpb_api_key else None

meter = otel_metrics.get_meter("h-crypto-price-bot.http")
api_calls_total = meter.create_counter(
    "bot.api.calls_total",
    unit="1",
    description="Total number of external API calls",
)
api_errors_total = meter.create_counter(
    "bot.api.errors_total",
    unit="1",
    description="Total number of external API call failures",
)
api_duration_seconds = meter.create_histogram(
    "bot.api.duration_seconds",
    unit="s",
    description="Duration of external API calls",
)
rate_limit_exceeded_total = meter.create_counter(
    "bot.rate_limit.exceeded_total",
    unit="1",
    description="Total number of rate limit blocks",
)


@logfire.instrument("fetch_url {url}")
async def fetch_url(
    url: str, headers: dict[str, str] | None = None, service: str = "unknown", timeout: float = 30.0
) -> dict | list | None:
    span = otel_trace.get_current_span()
    metric_attrs = {"api.service": service}
    api_calls_total.add(1, metric_attrs)
    started_at = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            span.set_attribute("http.response.status_code", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to fetch URL {url}, status code: {response.status_code}")
                api_errors_total.add(1, metric_attrs)
                return None
    except Exception as e:
        span.record_exception(e)
        logging.error(f"Error fetching URL {url}: {str(e)}")
        api_errors_total.add(1, metric_attrs)
        return None
    finally:
        api_duration_seconds.record(perf_counter() - started_at, metric_attrs)


@logfire.instrument("write_call service={service_id} type={type_id}")
async def write_call(service_id: int, type_id: int, chat_id: str, coin: str | None = None) -> bool:
    if not s.hcpb_api_url:
        return True
    span = otel_trace.get_current_span()
    span.set_attribute("chat.id", chat_id)
    if coin:
        span.set_attribute("coin.id", coin)
    url = f"{s.hcpb_api_url}/calls"
    data = {"service_id": service_id, "type_id": type_id, "chat_id": chat_id, "coin": coin}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=api_headers)
            if response.status_code != 401:
                span.set_attribute("rate_limited", False)
                return True
            else:
                span.set_attribute("rate_limited", True)
                rate_limit_exceeded_total.add(1, {"chat.id": chat_id})
                return False
    except Exception as e:
        span.record_exception(e)
        logging.error(f"Error tracking API: {str(e)}")
        return True


async def get_excluded() -> list[str]:
    url = f"{s.hcpb_api_url}/excluded"
    try:
        excluded = await fetch_url(url, headers=api_headers, service="hcpb-api")
        if not excluded:
            return []
        return excluded
    except Exception as e:
        logging.error(f"Error fetching excluded: {str(e)}")
        return []
