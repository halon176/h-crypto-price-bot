import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from src.handlers.callback import callback_handler
from src.handlers.cg_calls import get_cg_dominance, chart_color_handler, cg_price_handler, cg_chart_handler
from src.handlers.cmc_calls import cmc_key_info, cmc_price_handler
from src.handlers.ethersca_calls import gas_handler
from src.handlers.info import bot_help, start
from src.handlers.news import news
from src.utils.shared import CGCoinList, ChartTemplate, CMCCoinList
from .config import settings as s

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

cg_coin_list = CGCoinList()
cg_coin_list.update()

cmc_coin_list = CMCCoinList()
cmc_coin_list.update()

chart_template = ChartTemplate()

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


if __name__ == "__main__":
    if not s.API_URL:
        logging.info("API_URL not set, no calls control will be performed")

    application = ApplicationBuilder().token(s.TELEGRAM_TOKEN.get_secret_value()).build()

    for handler_name, handler in handlers.items():
        application.add_handler(CommandHandler(handler_name, handler))

    application.add_handler(CallbackQueryHandler(callback_handler))

    application.run_polling()
