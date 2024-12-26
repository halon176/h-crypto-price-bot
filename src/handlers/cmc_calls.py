import logging
from functools import reduce

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import settings as s
from src.utils.errors import send_error
from src.utils.formatters import human_format, max_column_size
from src.utils.shared import GeneralDataEntry, PriceChangeEntry, cmc_coin_list
from src.utils.http import write_call, fetch_url
from src.utils.bot import send_tg


headers = {"X-CMC_PRO_API_KEY": ""}

if s.CMC_API_KEY:
    headers["X-CMC_PRO_API_KEY"] = s.CMC_API_KEY.get_secret_value()

exp_message = (
    "You have reached the maximum number of requests for this period. It will be reset in the end of the month."
)


async def get_cmc_id(crypto_symbol: str) -> list[int]:
    """
    Get the id of a coin from the CoinMarketCap index
    :param crypto_symbol:
    :return:
    """
    crypto_symbol = crypto_symbol.upper()
    api_ids = []
    for crypto in cmc_coin_list.coin_list["data"]:
        if crypto["symbol"] == crypto_symbol:
            api_ids.append(crypto["id"])
    return api_ids


async def get_cmc_coin_info(coin_id: int) -> dict[str, str]:
    for crypto in cmc_coin_list.coin_list["data"]:
        if coin_id == crypto["id"]:
            return {"name": crypto["name"], "symbol": crypto["symbol"]}


async def get_cmc_price(coin_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the price grid of a coin from CoinMarketCap index
    :param coin_id: id of the coin in the CoinMarketCap index
    :param update:
    :param context:
    :return: None
    """
    r = await write_call(2, 1, str(update.effective_chat.id), str(coin_id))
    if not r:
        await send_tg(context, update.effective_chat.id, exp_message)
        return

    url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id={coin_id}"
    r = await fetch_url(url, headers)
    logging.info(f"Request CMC URL: {url}")

    crypto_data = r["data"][str(coin_id)]

    market_cap_rank = crypto_data["cmc_rank"]

    crypto_name = crypto_data["name"]
    symbol = crypto_data["symbol"]

    price = human_format(crypto_data["quote"]["USD"]["price"])

    price_change_data = {
        "24h": "percent_change_24h",
        "7d": "percent_change_7d",
        "30d": "percent_change_30d",
        "60d": "percent_change_60d",
        "90d": "percent_change_90d",
    }

    price_changes = []
    for label, data_key in price_change_data.items():
        value = crypto_data["quote"]["USD"].get(data_key)
        price_changes.append(PriceChangeEntry(label, value))

    lst_column_size_changes = [
        max_column_size([prc.strEntry for prc in price_changes]),
        max_column_size([prc.strPercentage for prc in price_changes]),
    ]

    str_format_prc = f"{{:{lst_column_size_changes[0]}}}    {{:>{lst_column_size_changes[1]}}}"
    price_change_message = "\n".join([str_format_prc.format(prc.strEntry, prc.strPercentage) for prc in price_changes])

    lst_str_header = (
        "-" * (len(lst_column_size_changes) + 2 + reduce(lambda a, b: a + b, lst_column_size_changes)) + "\n"
    )

    general_data_sheme = (
        ("💰", "M. Cap", "market_cap"),
        ("💵", "Circ. S", "circulating_supply"),
        ("🖨", "Total S", "total_supply"),
        ("🏦", "Max S", "max_supply"),
    )

    general_data = []
    for emoji, label, data_key in general_data_sheme:
        if data_key == "market_cap":
            value = crypto_data["quote"]["USD"].get(data_key, "N/A")
        else:
            value = crypto_data.get(data_key, "N/A")
        general_data.append(GeneralDataEntry(emoji, label, value))

    lst_column_size_gend = [
        2,
        max_column_size([gend.type for gend in general_data]),
        max_column_size([gend.value for gend in general_data]),
    ]

    str_format_gend = f"{{}} {{:{lst_column_size_gend[1]}}}   {{:>{lst_column_size_gend[2]}}}"
    general_data_message = "\n".join(
        [str_format_gend.format(gend.emoji, gend.type, gend.value) for gend in general_data]
    )

    message = (
        f"{market_cap_rank}° {crypto_name} {symbol}\n"
        f"`Price: {price}$`\n"
        f"`{lst_str_header}`"
        f"`{price_change_message}`\n"
        f"`{lst_str_header}`"
        f"`{general_data_message}`\n"
    )
    await send_tg(context, update.effective_chat.id, message, mk_parse=False)


async def cmc_key_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://pro-api.coinmarketcap.com/v1/key/info"
    r = await fetch_url(url, headers)
    logging.info(f"Request CMC Key Info: {url}")

    data = r["data"]
    credit_limit_monthly = data["plan"].get("credit_limit_monthly", "N/A")
    credit_limit_monthly_reset = (data["plan"].get("credit_limit_monthly_reset", "N/A")).lower()
    minute_requests_made = data["usage"]["current_minute"].get("requests_made", "N/A")
    minute_requests_left = data["usage"]["current_minute"].get("requests_left", "N/A")
    day_credits_made = data["usage"]["current_day"].get("credits_used", "N/A")
    day_credits_left = data["usage"]["current_day"].get("credits_left", "N/A")
    month_credits_used = data["usage"]["current_month"].get("credits_used", "N/A")
    month_credits_left = data["usage"]["current_month"].get("credits_left", "N/A")

    message = (
        f"CoinMarketCap Key Info\n"
        f"\n"
        f"`Your monthly credit limit is {credit_limit_monthly}`\n"
        f"`Minute requests count is {minute_requests_made} of {minute_requests_left}`\n"
        f"`Daily credits used are {day_credits_made} of {day_credits_left}`\n"
        f"`Monthly credits used are {month_credits_used} of {month_credits_left}`\n"
        f"`Monthly credits limit will be reset {credit_limit_monthly_reset}`\n"
    )

    await send_tg(context, update.effective_chat.id, message)


async def cmc_coin_check(coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | bool:
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
        text = "🟠 There are multiple coins with the same symbol, please select the desired one:"
        await send_tg(context, update.effective_chat.id, text, reply_markup=reply_markup)


async def cmc_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto_symbol = context.args[0].lower()
    coin = await cmc_coin_check(crypto_symbol, update, context)
    if coin:
        try:
            await get_cmc_price(coin, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await send_error("generic", update, context)
