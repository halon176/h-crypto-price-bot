import requests
from telegram import Update
from telegram.ext import ContextTypes

from config import CMC_API_KEY
from src.service import human_format


async def ogz_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = (requests.get("https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?slug=ogzclub",
                      headers={"X-CMC_PRO_API_KEY": CMC_API_KEY})).json()

    message = f'🐺 OGZ\n' \
              f'```\n' \
              f"$ {human_format(r['data']['25832']['quote']['USD']['price'])}\n" \
              f'--------------------------\n' \
              f"%1h:     {round(r['data']['25832']['quote']['USD']['percent_change_1h'])}%\n" \
              f"%24h:   {round(r['data']['25832']['quote']['USD']['percent_change_24h'])}%\n" \
              f"%7d:    {round(r['data']['25832']['quote']['USD']['percent_change_7d'])}%\n" \
              f"%30d:   {round(r['data']['25832']['quote']['USD']['percent_change_30d'])}%\n" \
              f"%60d:   {round(r['data']['25832']['quote']['USD']['percent_change_60d'])}%\n" \
              f"%90d:   {round(r['data']['25832']['quote']['USD']['percent_change_90d'])}%\n" \
              f'--------------------------\n' \
              f"volume h24: ${human_format(r['data']['25832']['quote']['USD']['volume_24h'])}\n" \
              f'```' \
              f"[Token Address](https://etherscan.io/token/0xb7bda6a89e724f63572ce68fddc1a6d1d5d24bcf?a=0xcf852bf2abad76e9ac8c0fe115246462ba883638)"

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)
