import logging
import warnings

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .callback import callback_handler
from .cg_calls import get_cg_chart, get_cg_dominance, get_cg_id, get_cg_price
from .cmc_calls import cmc_key_info, get_cmc_coin_info, get_cmc_id, get_cmc_price
from .config import API_URL, TELEGRAM_TOKEN
from .defilama_calls import get_defilama_price
from .errors import send_error
from .ethersca_calls import gas_handler
from .info import bot_help, start
from .news import news
from .shared import CGCoinList, ChartTemplate, CMCCoinList

# ignore FutureWarning from pandas, to be fixed in future releases
warnings.simplefilter("ignore", category=FutureWarning)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

cg_coin_list = CGCoinList()
cg_coin_list.update()

cmc_coin_list = CMCCoinList()
cmc_coin_list.update()

chart_template = ChartTemplate()


async def cmc_coin_check(coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> int | bool:
    error = "symbol"
    if len(coin) == 0:
        await send_error(error, update, context)
        return False
    coins = await get_cmc_id(coin)
    if not coins:
        cmc_coin_list.update()
        coins = await get_cmc_id(coin)
        if not coins:
            await send_error(error, update, context)
            return False
    if len(coins) == 1:
        return coins[0]
    else:
        keyboard = []
        for crypto in coins:
            coin_data = await get_cmc_coin_info(crypto)
            button = [InlineKeyboardButton(coin_data["name"], callback_data="cmc_" + str(crypto))]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🟠 There are multiple coins with the same symbol, please select the desired one:",
            reply_markup=reply_markup,
        )


async def gc_coin_check(coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> str:
    error = "symbol"
    coin_type = kwargs.get("type", None)
    if len(coin) == 0:
        await send_error(error, update, context)
        return False
    coins = await get_cg_id(coin)
    if not coins:
        cg_coin_list.update()
        coins = await get_cg_id(coin)
        if not coins:
            await send_error(error, update, context)
            return False

    if len(coins) == 1:
        return coins[0]
    elif coin_type == "chart":
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data="chart_" + crypto)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🟠 There are multiple coins with the same symbol, please select the desired one:",
            reply_markup=reply_markup,
        )
    else:
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data=crypto)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🟠 There are multiple coins with the same symbol, please select the desired one:",
            reply_markup=reply_markup,
        )


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto_symbol = context.args[0].lower()
    coin = await gc_coin_check(crypto_symbol, update, context)
    if coin:
        try:
            await get_cg_price(coin, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await send_error("generic", update, context)


async def cmc_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto_symbol = context.args[0].lower()
    coin = await cmc_coin_check(crypto_symbol, update, context)
    if coin:
        try:
            await get_cmc_price(coin, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await send_error("generic", update, context)


async def cg_chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto_symbol = context.args[0].lower()
    coin = await gc_coin_check(crypto_symbol, update, context, type="chart")
    if coin:
        await get_cg_chart(coin, update, context)


async def chart_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    themes = [
        ["🌕 white", "charttemplate_plotly_white"],
        ["🌑 dark", "charttemplate_plotly_dark"],
    ]
    keyboard = []
    for theme in themes:
        button = [InlineKeyboardButton(theme[0], callback_data=theme[1])]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="🟠 select desired chart theme",
        reply_markup=reply_markup,
    )


async def eth_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args[0]) == 42 and context.args[0].startswith("0x"):
        await get_defilama_price(context.args[0], "ethereum", update, context)
    else:
        await send_error("erc_contract", update, context)


async def bsc_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args[0]) == 42 and context.args[0].startswith("0x"):
        await get_defilama_price(context.args[0], "bsc", update, context)
    else:
        await send_error("bsc_contract", update, context)


if __name__ == "__main__":
    if not API_URL:
        logging.info("API_URL not set, no calls control will be performed")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    cg_price_handler = CommandHandler("p", cg_price_handler)
    application.add_handler(cg_price_handler)

    chart_handler = CommandHandler("c", cg_chart_handler)
    application.add_handler(chart_handler)

    eth_contract_handler_b = CommandHandler("eth", eth_contract_handler)
    application.add_handler(eth_contract_handler_b)

    bsc_contract_handler_b = CommandHandler("bsc", bsc_contract_handler)
    application.add_handler(bsc_contract_handler_b)

    chart_color = CommandHandler("chart_color", chart_color_handler)
    application.add_handler(chart_color)

    cmc_price_handler = CommandHandler("cmc", cmc_price_handler)
    application.add_handler(cmc_price_handler)

    cmc_key_info = CommandHandler("cmckey", cmc_key_info)
    application.add_handler(cmc_key_info)

    crypto_gas_handler = CommandHandler("gas", gas_handler)
    application.add_handler(crypto_gas_handler)

    crypto_dominance_handler = CommandHandler("dom", get_cg_dominance)
    application.add_handler(crypto_dominance_handler)

    news_handler = CommandHandler("news", news)
    application.add_handler(news_handler)

    help_handler = CommandHandler("help", bot_help)
    application.add_handler(help_handler)

    menu_handler = CallbackQueryHandler(callback_handler)
    application.add_handler(menu_handler)

    application.run_polling()
