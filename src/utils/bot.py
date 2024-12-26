import io
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from telegram.constants import ParseMode

from telegram.ext import ContextTypes
from src.utils.formatters import mk2_formatter


async def send_tg(
    ctx: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str | None = None,
    photo: str | io.BytesIO | None = None,
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
    disable_web_page_preview: bool = True,
    mk_parse: bool = True,
) -> None:
    try:
        send_kwargs = {
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
        print(f"Error sending message: {e}")
