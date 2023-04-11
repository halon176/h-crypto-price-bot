import logging

import humanize
import requests
from telegram import Update
from telegram.ext import ContextTypes

from service import format_date

CRYPTOGECKO_API_URL = 'https://api.coingecko.com/api/v3/coins/'


async def get_coin_list():
    coin_list = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=false")
    return coin_list.json()


async def get_cg_price(coin_list, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid crypto symbol.")
        return
    api_id = ""
    crypto_symbol = context.args[0]
    for crypto in coin_list:
        if crypto["symbol"] == crypto_symbol:
            api_id = crypto["id"]
            break

    url_tail = '?localization=false&' \
               'tickers=false&market_data=true&' \
               'community_data=false' \
               '&developer_data=false' \
               '&sparkline=false'

    url = CRYPTOGECKO_API_URL + api_id + url_tail
    logging.info(f'Request URL: {url}')
    if api_id == "":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid crypto symbol.")
        return
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

    price_change_percentage_24h = round(crypto_data['market_data']['price_change_percentage_24h'], 1)
    price_change_percentage_7d = round(crypto_data['market_data']['price_change_percentage_7d'], 1)
    price_change_percentage_14d = round(crypto_data['market_data']['price_change_percentage_14d'], 1)
    price_change_percentage_30d = round(crypto_data['market_data']['price_change_percentage_30d'], 1)
    price_change_percentage_60d = round(crypto_data['market_data']['price_change_percentage_60d'], 1)
    price_change_percentage_200d = round(crypto_data['market_data']['price_change_percentage_200d'], 1)
    price_change_percentage_1y = round(crypto_data['market_data']['price_change_percentage_1y'], 1)

    market_cap = humanize.intword(crypto_data['market_data']['market_cap']["usd"])
    circulating_supply = humanize.intword(crypto_data['market_data']['circulating_supply'])
    total_supply = humanize.intword(crypto_data['market_data']['total_supply'])
    ath = humanize.intcomma(crypto_data['market_data']['ath']["usd"])
    ath_change_percentage = round(crypto_data['market_data']['ath_change_percentage']["usd"], 1)
    ath_date = format_date(crypto_data['market_data']['ath_date']["usd"])
    atl = humanize.intcomma(crypto_data['market_data']['atl']["usd"])
    atl_change_percentage = round(crypto_data['market_data']['atl_change_percentage']["usd"], 1)
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
              f"📈 ATH  {ath}$  ({ath_change_percentage}%) {ath_date}\n" \
              f"📉 ATL  {atl}$  ({atl_change_percentage}%) {atl_date}\n" \
              f"```"

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)
