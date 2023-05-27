from functools import reduce

import requests
from telegram import Update
from telegram.ext import ContextTypes

from config import CMC_API_KEY
from service import human_format, max_column_size
from shared import CMCCoinList

coin_list = CMCCoinList()


async def get_cmc_id(crypto_symbol: str):
    crypto_symbol = crypto_symbol.upper()
    api_ids = []
    for crypto in coin_list.coin_list["data"]:
        if crypto["symbol"] == crypto_symbol:
            api_ids.append(crypto["id"])
    return api_ids


async def get_cmc_price(coin, update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = (requests.get(f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id={coin}",
                      headers={"X-CMC_PRO_API_KEY": CMC_API_KEY})).json()
    crypto_data = r["data"][str(coin)]

    market_cap_rank = crypto_data['cmc_rank']

    crypto_name = crypto_data['name']
    symbol = crypto_data['symbol']

    price = human_format(crypto_data['quote']['USD']['price'])

    price_change_data = {
        "24h": "percent_change_24h",
        "7d": "percent_change_7d",
        "30d": "percent_change_30d",
        "60d": "percent_change_60d",
        "90d": "percent_change_90d",
    }

    class PriceChangeEntry:
        def __init__(self, change_label, change_value):
            self.strEntry = change_label
            if change_value is None:
                self.strPercentage = "N/A"
            else:
                self.strPercentage = f"{change_value:.1f}%"

    price_changes = []
    for label, data_key in price_change_data.items():
        value = crypto_data['quote']['USD'].get(data_key)
        price_changes.append(PriceChangeEntry(label, value))

    lst_column_size_changes = [
        max_column_size((prc.strEntry for prc in price_changes)),
        max_column_size((prc.strPercentage for prc in price_changes))
    ]

    str_format_prc = f"{{:{lst_column_size_changes[0]}}}    {{:>{lst_column_size_changes[1]}}}"
    price_change_message = "\n".join([str_format_prc.format(prc.strEntry, prc.strPercentage) for prc in price_changes])

    lst_str_header = "-" * (len(lst_column_size_changes) + 2 + reduce(lambda a, b: a + b, lst_column_size_changes)) \
                     + "\n"

    general_data_sheme = (("💰", "M. Cap", "market_cap"),
                          ("💵", "Circ. S", "circulating_supply"),
                          ("🖨", "Total S", "total_supply"),
                          ("🏦", "Max S", "max_supply"),
                          )

    class GeneralDataEntry:
        def __init__(self, data_emoji, data_type, data_value):
            self.emoji = data_emoji
            self.type = data_type
            if value == "N/A" or value is None:
                self.value = "N/A"
            else:
                self.value = human_format(float(data_value))

    general_data = []
    for emoji, label, data_key in general_data_sheme:
        if data_key == "market_cap":
            value = crypto_data['quote']['USD'].get(data_key, "N/A")
        else:
            value = crypto_data.get(data_key, "N/A")
        general_data.append(GeneralDataEntry(emoji, label, value))

    lst_column_size_gend = [
        2,
        max_column_size((gend.type for gend in general_data)),
        max_column_size((gend.value for gend in general_data))
    ]

    str_format_gend = f"{{}} {{:{lst_column_size_gend[1]}}}   {{:>{lst_column_size_gend[2]}}}"
    general_data_message = "\n".join(
        [str_format_gend.format(gend.emoji, gend.type, gend.value) for gend in general_data])

    message = f"{market_cap_rank}° {crypto_name} {symbol}\n" \
              f"```\n" \
              f"Price: {price}$\n" \
              f"{lst_str_header}" \
              f"{price_change_message}\n" \
              f"{lst_str_header}" \
              f"{general_data_message}\n" \
              f"```"
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)


async def ogz_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_cmc_price('25832', update, context)
