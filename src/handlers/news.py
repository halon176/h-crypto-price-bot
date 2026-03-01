import logfire
import feedparser
from telegram import Update
from telegram.ext import ContextTypes

from src.utils.bot import send_tg

RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"


@logfire.instrument("news_handler")
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    feed = feedparser.parse(RSS_URL)

    latest_entries = feed.entries[:7]
    message = "    📰 News feed from CoinDesk 📰\n\n"
    for entry in latest_entries:
        message += f"🗞️ [{entry['title']}]({entry['link']})\n\n"

    await send_tg(context, update.effective_chat.id, message)
