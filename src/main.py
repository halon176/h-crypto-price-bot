import asyncio
import logging

import logfire
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

logfire.configure(
    token=s.LOGFIRE_TOKEN.get_secret_value() if s.LOGFIRE_TOKEN else None,
    service_name="h-crypto-price-bot",
    distributed_tracing=True,
)
logfire.instrument_httpx()


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
        application.add_handler(CommandHandler(handler_name, handler))

    application.add_handler(CallbackQueryHandler(callback_handler))

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
