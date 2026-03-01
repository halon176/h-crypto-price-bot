import feedparser
import logfire
from opentelemetry import trace as otel_trace
from telegram import Update
from telegram.ext import ContextTypes

from src.utils.bot import send_tg

RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"


@logfire.instrument("news_handler")
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    span = otel_trace.get_current_span()
    span.set_attribute("chat.id", str(update.effective_chat.id))
    span.set_attribute("user.id", str(update.effective_user.id))

    feed = feedparser.parse(RSS_URL)

    latest_entries = feed.entries[:7]
    span.set_attribute("news.count", len(latest_entries))

    message = "    📰 News feed from CoinDesk 📰\n\n"
    for entry in latest_entries:
        message += f"🗞️ [{entry['title']}]({entry['link']})\n\n"

    await send_tg(context, update.effective_chat.id, message)
