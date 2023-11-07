import logging
from functools import reduce

from telegram import Update
from telegram.ext import ContextTypes

from src.config import CMC_API_KEY
from src.models import PriceChangeEntry, GeneralDataEntry
from src.shared import CMCCoinList
from src.utility import human_format, max_column_size, fetch_url

coin_list = CMCCoinList()
headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}


async def get_cmc_id(crypto_symbol: str):
    crypto_symbol = crypto_symbol.upper()
    api_ids = []
    for crypto in coin_list.coin_list["data"]:
        if crypto["symbol"] == crypto_symbol:
            api_ids.append(crypto["id"])
    return api_ids


async def get_cmc_coin_info(coin_id: int):
    for crypto in coin_list.coin_list["data"]:
        if coin_id == crypto["id"]:
            return {"name": crypto["name"], "symbol": crypto["symbol"]}


async def get_cmc_price(coin, update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id={coin}"
    r = await fetch_url(url, headers)
    logging.info(f"Request CMC URL: {url}")

    crypto_data = r["data"][str(coin)]

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
        max_column_size((prc.strEntry for prc in price_changes)),
        max_column_size((prc.strPercentage for prc in price_changes)),
    ]

    str_format_prc = (
        f"{{:{lst_column_size_changes[0]}}}    {{:>{lst_column_size_changes[1]}}}"
    )
    price_change_message = "\n".join(
        [
            str_format_prc.format(prc.strEntry, prc.strPercentage)
            for prc in price_changes
        ]
    )

    lst_str_header = (
            "-"
            * (
                    len(lst_column_size_changes)
                    + 2
                    + reduce(lambda a, b: a + b, lst_column_size_changes)
            )
            + "\n"
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
        max_column_size((gend.type for gend in general_data)),
        max_column_size((gend.value for gend in general_data)),
    ]

    str_format_gend = (
        f"{{}} {{:{lst_column_size_gend[1]}}}   {{:>{lst_column_size_gend[2]}}}"
    )
    general_data_message = "\n".join(
        [
            str_format_gend.format(gend.emoji, gend.type, gend.value)
            for gend in general_data
        ]
    )

    message = (
        f"{market_cap_rank}° {crypto_name} {symbol}\n"
        f"\n"
        f"`Price: {price}$`\n"
        f"`{lst_str_header}`"
        f"`{price_change_message}`\n"
        f"`{lst_str_header}`"
        f"`{general_data_message}`\n"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


async def cmc_key_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://pro-api.coinmarketcap.com/v1/key/info"
    r = await fetch_url(url, headers)
    logging.info(f"Request CMC Key Info: {url}")

    data = r["data"]
    credit_limit_monthly = data["plan"].get("credit_limit_monthly", "N/A")
    credit_limit_monthly_reset = (
        data["plan"].get("credit_limit_monthly_reset", "N/A")
    ).lower()
    minut_requests_made = data["usage"]["current_minute"].get("requests_made", "N/A")
    minut_requests_left = data["usage"]["current_minute"].get("requests_left", "N/A")
    day_credits_made = data["usage"]["current_day"].get("credits_used", "N/A")
    day_credits_left = data["usage"]["current_day"].get("credits_left", "N/A")
    month_credits_used = data["usage"]["current_month"].get("credits_used", "N/A")
    month_credits_left = data["usage"]["current_month"].get("credits_left", "N/A")

    message = (
        f"CoinMarketCap Key Info\n"
        f"\n"
        f"`Your monthly credit limit is {credit_limit_monthly}`\n"
        f"`Minut requests count is {minut_requests_made} of {minut_requests_left}`\n"
        f"`Daily credits used are {day_credits_made} of {day_credits_left}`\n"
        f"`Monthly credits used are {month_credits_used} of {month_credits_left}`\n"
        f"`Monthly credits limit will be reset {credit_limit_monthly_reset}`\n"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
