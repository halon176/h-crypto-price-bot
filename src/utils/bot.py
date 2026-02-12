"""Telegram bot messaging utilities."""

import io
import logging
from typing import Any

from telegram import ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.utils.formatters import mk2_formatter

logger = logging.getLogger(__name__)


async def send_tg(
    ctx: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str | None = None,
    photo: str | io.BytesIO | None = None,
    reply_markup: (
        InlineKeyboardMarkup
        | ReplyKeyboardMarkup
        | ReplyKeyboardRemove
        | ForceReply
        | None
    ) = None,
    disable_web_page_preview: bool = True,
    mk_parse: bool = True,
) -> None:
    """Send a message or photo to a Telegram chat.

    Args:
        ctx: Telegram context
        chat_id: Chat ID to send message to
        text: Optional text content
        photo: Optional photo (file path or BytesIO object)
        reply_markup: Optional keyboard markup
        disable_web_page_preview: Whether to disable web page previews
        mk_parse: Whether to apply MarkdownV2 formatting to text

    Raises:
        Exception: If message sending fails after retries
    """
    try:
        send_kwargs: dict[str, Any] = {
            "chat_id": chat_id,
            "reply_markup": reply_markup,
            "parse_mode": ParseMode.MARKDOWN_V2,
        }

        if mk_parse and text:
            text = mk2_formatter(text)

        if photo:
            send_kwargs["photo"] = photo
            send_kwargs["caption"] = text
            await ctx.bot.send_photo(**send_kwargs)
        else:
            send_kwargs["disable_web_page_preview"] = disable_web_page_preview
            send_kwargs["text"] = text
            await ctx.bot.send_message(**send_kwargs)

    except Exception as e:
        logger.error(f"Error sending message to chat {chat_id}: {e}", exc_info=True)
