import logging
import os
from functools import reduce

import humanize
import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from service import format_date, max_column_size, at_handler, k_handler

CRYPTOGECKO_API_COINS = 'https://api.coingecko.com/api/v3/coins/'
CRYPTOGECKO_API_DOMINANCE = 'https://api.coingecko.com/api/v3/global/'

coin_list_gc = []


class ChartTemplate:
    _instance = None
    template = 'plotly_dark'

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_template(cls, template: str):
        cls.template = template

    def get_template(self):
        return self.template


chart_template = ChartTemplate()


async def get_coin_list():
    global coin_list_gc
    coin_request = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=false")
    if coin_request.status_code == 200:
        coin_list_gc = coin_request.json()
        return coin_list_gc
    else:
        return "request_error"


async def get_api_id(crypto_symbol: str, coin_list):
    excluded_values = ["-peg-", "-wormhole", "wrapped", "oec-", "-iou", "harrypotter"]
    api_ids = []
    for crypto in coin_list:
        if crypto["symbol"] == crypto_symbol and all(excluded not in crypto["id"] for excluded in excluded_values):
            api_ids.append(crypto["id"])
    return api_ids


async def get_coin_info(coin_name: str):
    for crypto in coin_list_gc:
        if coin_name == crypto['id']:
            return {'name': crypto['name'], 'symbol': crypto['symbol'].upper()}


async def get_cg_price(coin, update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_tail = '?localization=false&' \
               'tickers=false&market_data=true&' \
               'community_data=false' \
               '&developer_data=false' \
               '&sparkline=false'

    url = CRYPTOGECKO_API_COINS + coin + url_tail
    logging.info(f'Request URL: {url}')

    response = requests.get(url)

    if response.status_code != 200:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="An error occurred. Please try again later.")
        return

    crypto_data = response.json()

    if len(crypto_data) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid crypto symbol.")
        return

    if crypto_data['market_cap_rank'] is None:
        market_cap_rank = ""
    else:
        market_cap_rank = str(crypto_data['market_cap_rank']) + "°"
    crypto_name = crypto_data['name']
    usd_price = crypto_data['market_data']['current_price'].get('usd')
    crypto_price = humanize.intcomma(usd_price) if usd_price is not None else 'N/A'

    try:
        index_of_ref = crypto_data['links']['homepage'][0].index("?")
        web = crypto_data['links']['homepage'][0][:index_of_ref]
    except ValueError:
        web = crypto_data['links']['homepage'][0]

    twitter = "https://twitter.com/" + crypto_data['links']["twitter_screen_name"]
    symbol = (crypto_data['symbol']).upper()

    price_change_data = {
        "24h": "price_change_percentage_24h",
        "7d": "price_change_percentage_7d",
        "14d": "price_change_percentage_14d",
        "30d": "price_change_percentage_30d",
        "60d": "price_change_percentage_60d",
        "200d": "price_change_percentage_200d",
        "1y": "price_change_percentage_1y",
    }
    general_data_sheme = (("💰", "M. Cap", "market_cap"),
                          ("💵", "Circ. S", "circulating_supply"),
                          ("🖨", "Total S", "total_supply"))

    class GeneralDataEntry:
        def __init__(self, data_emoji, data_type, data_value):
            self.emoji = data_emoji
            self.type = data_type
            if value is None:
                self.value = "N/A"
            else:
                self.value = humanize.intword(data_value)

    general_data = []
    for emoji, label, data_key in general_data_sheme:
        if data_key == "market_cap":
            value = crypto_data['market_data'].get(data_key, {}).get("usd", "N/A")
        else:
            value = crypto_data['market_data'].get(data_key, "N/A")
        general_data.append(GeneralDataEntry(emoji, label, value))

    lst_column_size_gend = [
        2,
        max_column_size((gend.type for gend in general_data)),
        max_column_size((gend.value for gend in general_data))
    ]

    str_format_gend = f"{{}} {{:{lst_column_size_gend[1]}}}   {{:>{lst_column_size_gend[2]}}}"
    general_data_message = "\n".join(
        [str_format_gend.format(gend.emoji, gend.type, gend.value) for gend in general_data])

    class PriceChangeEntry:
        def __init__(self, change_label, change_value):
            self.strEntry = change_label
            if change_value is None:
                self.strPercentage = "N/A"
            else:
                self.strPercentage = f"{change_value:.1f}%"

    price_changes = []
    for label, data_key in price_change_data.items():
        value = crypto_data['market_data'].get(data_key)
        price_changes.append(PriceChangeEntry(label, value))

    lst_column_size_changes = [
        max_column_size((prc.strEntry for prc in price_changes)),
        max_column_size((prc.strPercentage for prc in price_changes))
    ]

    str_format_prc = f"{{:{lst_column_size_changes[0]}}}    {{:>{lst_column_size_changes[1]}}}"
    price_change_message = "\n".join([str_format_prc.format(prc.strEntry, prc.strPercentage) for prc in price_changes])

    at_data_schema = (("📈", "ATH", "ath", "ath_change_percentage", "ath_date"),
                      ("📉", "ATL", "atl", "atl_change_percentage", "atl_date"))

    class AtEntry:
        def __init__(self, allt_emoji, allt_symbol, allt_price, allt_percentage, allt_date):
            self.emoji = allt_emoji
            self.symbol = allt_symbol
            if allt_price and "usd" in allt_price:
                self.at_price = humanize.intcomma(at_handler(allt_price["usd"])) + "$"
            else:
                self.at_price = "N/A"
            if allt_percentage and "usd" in allt_percentage:
                self.at_percentage = k_handler(allt_percentage["usd"]) + "%"
            else:
                self.at_percentage = "N/A"
            if allt_date and "usd" in allt_date:
                self.date = format_date(allt_date["usd"])
            else:
                self.date = "N/A"

    at_data = []
    for emoji, label, price, percentage, date in at_data_schema:
        at_price = crypto_data['market_data'][price]
        at_percentage = crypto_data['market_data'][percentage]
        at_date = crypto_data['market_data'][date]
        at_data.append(AtEntry(emoji, label, at_price, at_percentage, at_date))

    lst_column_size_at = [
        2,
        max_column_size((at.symbol for at in at_data)),
        max_column_size((at.at_price for at in at_data)),
        max_column_size((at.at_percentage for at in at_data)),
        max_column_size((at.date for at in at_data))
    ]

    str_format_at = f"{{:{lst_column_size_at[0]}}}{{:{lst_column_size_at[1]}}} {{:>{lst_column_size_at[2]}}}" \
                    f" ({{:>{lst_column_size_at[3]}}}) {{:>{lst_column_size_at[4]}}}"

    at_data_message = "\n".join([str_format_at.format(atd.emoji, atd.symbol, atd.at_price, atd.at_percentage, atd.date)
                                 for atd in at_data])

    lst_str_header = "-" * (len(lst_column_size_changes) + 2 + reduce(lambda a, b: a + b, lst_column_size_changes)) \
                     + "\n"

    message = f"{market_cap_rank} [{crypto_name}]({web}) [{symbol}]({twitter})\n" \
              f"```\n" \
              f"Price: {crypto_price}$\n" \
              f"{lst_str_header}" \
              f"{price_change_message}\n" \
              f"{lst_str_header}" \
              f"{general_data_message}\n" \
              f"{at_data_message}" \
              f"```"

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)


async def get_cg_chart(coin, update: Update, context: ContextTypes.DEFAULT_TYPE, period='30'):
    url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={period}'
    chart = requests.get(url).json()
    logging.info(f'Request URL: {url}')
    x = [p[0] / 1000 for p in chart['prices']]
    y = [p[1] for p in chart['prices']]

    df = pd.DataFrame({'timeframe': x, 'prices': y})
    df['timeframe'] = pd.to_datetime(df['timeframe'], unit='s')
    info = await get_coin_info(coin)
    title = f'{info["name"]} ({info["symbol"]})'
    bottom = f'{period} day{"s" if period != "1" else ""} chart'
    template = chart_template.get_template()
    fig = px.line(df, x='timeframe', y='prices', template=template,
                  labels={'timeframe': bottom, 'prices': 'price ($)'})

    fig.update_layout(
        title={
            'text': title,
            'y': 0.93,
            'x': 0.5,
            'font': dict(size=24)
        }
    )

    pio.write_image(fig, 'plot.jpg', format='jpg')

    periods = [{'1': '24h'}, {'7': '7d'}, {'30': '30d'}, {'90': '90d'}, {'365': '1y'}, {'max': 'max'}]
    checkbox = [''] * 6

    for i in range(len(periods)):
        current_key = list(periods[i].keys())[0]
        if period == current_key:
            checkbox[i] = '✅'

    keyboard = [[InlineKeyboardButton(f"{checkbox[i]}{list(periods[i].values())[0]}",
                                      callback_data=f'period_{list(periods[i].keys())[0]}.{coin}') for i in
                 range(len(periods))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('plot.jpg', 'rb'),
                                 reply_markup=reply_markup)
    os.remove('plot.jpg')


async def get_cg_dominance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(CRYPTOGECKO_API_DOMINANCE)
    if response.status_code != 200:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="An error occurred. Please try again later.")
        return
    global_data = response.json()
    logging.info(f'Request coin dominance list')

    positional_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    dom_percentage = list(global_data["data"]["market_cap_percentage"].items())

    class MarketCapEntry:
        def __init__(self, tplSymbolPercentage):
            self.strSymbol = tplSymbolPercentage[0].upper()
            self.strPercentage = f"{tplSymbolPercentage[1]:.1f}%"

    lstmkp = [MarketCapEntry(tplSymbolPercentage) for tplSymbolPercentage in dom_percentage]

    lst_column_size = [
        2,
        max_column_size((mkp.strSymbol for mkp in lstmkp)),
        max_column_size((mkp.strPercentage for mkp in lstmkp))
    ]

    lst_str_header = [
        "```",
        "-" * (len(lst_column_size) + reduce(lambda a, b: a + b, lst_column_size))
    ]
    str_format = f"{{}}  {{:{lst_column_size[1]}}} {{:>{lst_column_size[2]}}}"
    message = "\n".join(
        [f"🏆 TOP {len(lstmkp)} MARKETCAP 🏆"]
        + lst_str_header
        + [
            str_format.format(str_emoji, mkp.strSymbol, mkp.strPercentage)
            for str_emoji, mkp in zip(positional_emoji, lstmkp)
        ]
        + list(reversed(lst_str_header))
    )

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)
