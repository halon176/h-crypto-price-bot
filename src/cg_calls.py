import logging
from functools import reduce

import humanize
import requests
from telegram import Update
from telegram.ext import ContextTypes

from service import format_date

CRYPTOGECKO_API_COINS = 'https://api.coingecko.com/api/v3/coins/'
CRYPTOGECKO_API_DOMINANCE = 'https://api.coingecko.com/api/v3/global/'


async def get_coin_list():
    coin_list = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=false")
    if coin_list.status_code == 200:
        return coin_list.json()
    else:
        return "request_error"


async def get_api_id(crypto_symbol: str, coin_list):
    api_ids = []
    for crypto in coin_list:
        if crypto["symbol"] == crypto_symbol and "-peg-" not in crypto["id"]:
            api_ids.append(crypto["id"])
    if not api_ids:
        return "symbol_error"
    else:
        return api_ids


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

    market_cap_rank = crypto_data['market_cap_rank']
    crypto_name = crypto_data['name']
    crypto_price = humanize.intcomma(crypto_data['market_data']['current_price']["usd"])
    web = crypto_data['links']['homepage'][0]
    twitter = "https://twitter.com/" + crypto_data['links']["twitter_screen_name"]
    symbol = (crypto_data['symbol']).upper()
    if not crypto_data['market_data']['price_change_percentage_24h']:
        price_change_percentage_24h = "N/A"
    else:
        price_change_percentage_24h = round(crypto_data['market_data']['price_change_percentage_24h'], 1)
    price_change_percentage_7d = round(crypto_data['market_data']['price_change_percentage_7d'], 1)
    price_change_percentage_14d = round(crypto_data['market_data']['price_change_percentage_14d'], 1)
    price_change_percentage_30d = round(crypto_data['market_data']['price_change_percentage_30d'], 1)
    price_change_percentage_60d = round(crypto_data['market_data']['price_change_percentage_60d'], 1)
    price_change_percentage_200d = round(crypto_data['market_data']['price_change_percentage_200d'], 1)
    price_change_percentage_1y = round(crypto_data['market_data']['price_change_percentage_1y'], 1)

    if not crypto_data['market_data']['market_cap']:
        market_cap = "N/A"
    else:
        market_cap = humanize.intword(crypto_data['market_data']['market_cap']["usd"])
    circulating_supply = humanize.intword(crypto_data['market_data']['circulating_supply'])
    total_supply = humanize.intword(crypto_data['market_data']['total_supply'])
    if not crypto_data['market_data']['ath']["sgd"]:
        ath = "N/A"
    else:
        ath = humanize.intcomma(crypto_data['market_data']['ath']["usd"])
    ath_change_percentage = round(crypto_data['market_data']['ath_change_percentage']["usd"], 1)
    if not crypto_data['market_data']['ath_date']['sgd']:
        ath_date = "N/A"
    else:
        ath_date = format_date(crypto_data['market_data']['ath_date']["usd"])
    if not crypto_data['market_data']['atl']:
        atl = "N/A"
    else:
        atl = humanize.intcomma(crypto_data['market_data']['atl']["usd"])
    atl_change_percentage = round(crypto_data['market_data']['atl_change_percentage']["usd"], 1)
    if not crypto_data['market_data']['atl_date']:
        atl_date = "N/A"
    else:
        atl_date = format_date(crypto_data['market_data']['atl_date']["usd"])

    message = f"{market_cap_rank}° [{crypto_name}]({web}) [{symbol}]({twitter})\n" \
              f"```\n" \
              f"Price: {crypto_price}$\n" \
              f"-----------------------------\n" \
              f"24h:     {price_change_percentage_24h}%\n" \
              f"7d:      {price_change_percentage_7d}%\n" \
              f"14d:     {price_change_percentage_14d}%\n" \
              f"30d:     {price_change_percentage_30d}%\n" \
              f"60d:     {price_change_percentage_60d}%\n" \
              f"200d:    {price_change_percentage_200d}%\n" \
              f"1y:      {price_change_percentage_1y}%\n" \
              f"-----------------------------\n" \
              f"💰 M. Cap     {market_cap}\n" \
              f"💵 Circ. S    {circulating_supply}\n" \
              f"🖨 Total S    {total_supply}\n" \
              f"📈 ATH {ath}$ ({ath_change_percentage}%) {ath_date}\n" \
              f"📉 ATL {atl}$ ({atl_change_percentage}%) {atl_date}\n" \
              f"```"

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)


async def get_cg_dominance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(CRYPTOGECKO_API_DOMINANCE)
    if response.status_code != 200:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="An error occurred. Please try again later.")
        return
    global_data = response.json()
    logging.info(f'Request coin dominance list')

    lst_str_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    dom_percentage = list(global_data["data"]["market_cap_percentage"].items())

    class MarketCapEntry:
        def __init__(self, tplSymbolPercentage):
            self.strSymbol = tplSymbolPercentage[0].upper()
            self.strPercentage = f"{tplSymbolPercentage[1]:.1f}%"

    lstmkp = [MarketCapEntry(tplSymbolPercentage) for tplSymbolPercentage in dom_percentage]

    def columnSize(lststr):
        return max((len(string) for string in lststr))

    lst_column_size = [
        2,
        columnSize((mkp.strSymbol for mkp in lstmkp)),
        columnSize((mkp.strPercentage for mkp in lstmkp))
    ]

    lst_str_header = [
        "```",
        "-" * (len(lst_column_size) - 1 + reduce(lambda a, b: a + b, lst_column_size))
    ]
    str_format = f"{{}}  {{:{lst_column_size[1]}}}{{:>{lst_column_size[2]}}}"
    message = "\n".join(
        [f"🏆 TOP {len(lstmkp)} MARKETCAP 🏆"]
        + lst_str_header
        + [
            str_format.format(str_emoji, mkp.strSymbol, mkp.strPercentage)
            for str_emoji, mkp in zip(lst_str_emoji, lstmkp)
        ]
        + list(reversed(lst_str_header))
    )

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)
