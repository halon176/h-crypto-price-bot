import asyncio
import logging
import re
from functools import wraps
from time import perf_counter
from typing import Any

import logfire
from logfire import ScrubbingOptions, ScrubMatch
from opentelemetry import metrics
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from src.handlers.callback import callback_handler
from src.handlers.cg_calls import cg_chart_handler, cg_price_handler, chart_color_handler, get_cg_dominance
from src.handlers.cmc_calls import cmc_key_info, cmc_price_handler
from src.handlers.ethersca_calls import gas_handler
from src.handlers.info import bot_help, start
from src.handlers.news import news
from src.utils.shared import cg_coin_list, cmc_coin_list

from .config import settings as s

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

meter = metrics.get_meter("h-crypto-price-bot")
handler_calls_total = meter.create_counter(
    "bot.handler.calls_total",
    unit="1",
    description="Total number of Telegram handler calls",
)
handler_errors_total = meter.create_counter(
    "bot.handler.errors_total",
    unit="1",
    description="Total number of Telegram handler errors",
)
handler_duration_seconds = meter.create_histogram(
    "bot.handler.duration_seconds",
    unit="s",
    description="Execution time of Telegram handlers",
)


def _scrub_callback(match: ScrubMatch) -> str | None:
    """Redact API key values embedded in URLs (e.g. ?apikey=SECRET) instead of the full URL."""
    if isinstance(match.value, str) and re.search(r"apikey=", match.value, re.IGNORECASE):
        return re.sub(r"(?i)(apikey)=[^&\s#]+", r"\1=[REDACTED]", match.value)
    return None


logfire.configure(
    token=s.LOGFIRE_TOKEN.get_secret_value() if s.LOGFIRE_TOKEN else None,
    service_name="h-crypto-price-bot",
    distributed_tracing=True,
    scrubbing=ScrubbingOptions(callback=_scrub_callback),
)
logfire.instrument_httpx()


def _instrument_handler(handler_name: str, handler_type: str, handler: Any):
    @wraps(handler)
    async def wrapped(update, context):
        attributes = {"handler.name": handler_name, "handler.type": handler_type}
        started_at = perf_counter()
        handler_calls_total.add(1, attributes)

        try:
            return await handler(update, context)
        except Exception:
            handler_errors_total.add(1, attributes)
            raise
        finally:
            handler_duration_seconds.record(perf_counter() - started_at, attributes)

    return wrapped


async def setup_bot():
    await cmc_coin_list.update()
    await cg_coin_list.update()

    handlers = {
        "start": start,
        "p": cg_price_handler,
        "c": cg_chart_handler,
        "chart_color": chart_color_handler,
        "cmc": cmc_price_handler,
        "cmckey": cmc_key_info,
        "gas": gas_handler,
        "dom": get_cg_dominance,
        "news": news,
        "help": bot_help,
    }

    application = ApplicationBuilder().token(s.TELEGRAM_TOKEN.get_secret_value()).build()

    for handler_name, handler in handlers.items():
        application.add_handler(CommandHandler(handler_name, _instrument_handler(handler_name, "command", handler)))

    application.add_handler(CallbackQueryHandler(_instrument_handler("callback_handler", "callback", callback_handler)))

    return application


if __name__ == "__main__":
    if not s.hcpb_api_url:
        logging.info("API_URL not set, no calls control will be performed")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot = loop.run_until_complete(setup_bot())

    if s.WEBHOOK_URL:
        logging.info(f"Starting webhook mode on port {s.WEBHOOK_PORT} → {s.WEBHOOK_URL}")
        bot.run_webhook(
            listen="0.0.0.0",
            port=s.WEBHOOK_PORT,
            url_path="webhook",
            webhook_url=s.WEBHOOK_URL,
            secret_token=s.WEBHOOK_SECRET_TOKEN.get_secret_value() if s.WEBHOOK_SECRET_TOKEN else None,
        )
    else:
        logging.info("Starting polling mode (no WEBHOOK_URL set)")
        bot.run_polling()
