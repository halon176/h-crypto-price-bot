import feedparser

from telegram import Update
from telegram.ext import ContextTypes

RSS_URL = "https://cointelegraph.com/editors_pick_rss"


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feed = feedparser.parse(RSS_URL)
    latest_entries = feed.entries[:7]
    message = "    📰 Editors pick from CoinTelegraph 📰\n\n"
    for entry in latest_entries:
        message += f"🗞️ [{entry['title']}]({entry['link']})\n\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
