import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.utility import fetch_url


async def get_defilama_price(
        contract, chain, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    url = f"https://coins.llama.fi/prices/current/{chain}:{contract}?searchWidth=1h"
    response = await fetch_url(url)
    if not response["coins"]:
        error_message = "⚠ no coin found with this contract"
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=error_message, parse_mode="MarkdownV2"
        )
        return
    else:
        logging.info(f"Request URL: {url}")
        coin = list(response["coins"].values())[0]
        message = (
            f"\n"
            f'`{coin["symbol"].upper()} on {chain.upper()}`\n'
            f'`price = {coin["price"]}$`'
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message, parse_mode="MarkdownV2"
        )
