import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from .utility import mk2_formatter


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response_text = (
        "Hi! I am HCryptoPrice, You can ask me for the current price of any crypto by typing:\n\n"
        "`/p <crypto_symbol>` \n\n"
        "For example, `/p btc` will give you the current price of Bitcoin. Enjoy!\n\n"
        "To display the complete list of commands, type `/help`"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        text=mk2_formatter(response_text),
    )
    logging.info("Start call")


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response_text = (
        "📚*List of Commands:*\n\n"
        "`/p <crypto_symbol>` - to receive the current price and historical variation from CoinCecko\n"
        "`/c <crypto_symbol>` - to receive the chart in different timeframes of selected crypto\n"
        "`/cmc <crypto_symbol>` - to receive the current price and historical variation from CoinMarketCap\n"
        "`/chart_color` - to select chart color theme\n"
        "/cmckey - to receive info about CoinMarketCap api key usage\n"
        "/dom - to receive the top 10 most capitalized tokens\n"
        "/gas - to receive real-time gas information on ERC\n"
        "/news - to receive CoinDesk news\n"
        "/help - to receive this message\n\n"
        "This bot is written with open-source and free code, and you can find it all at "
        "[GitHub](https://github.com/halon176/h-crypto-price-bot)\n\n"
        "`Bot version: 1.2.1`\n"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
        text=mk2_formatter(response_text),
    )

    logging.info("Help call")
