from telegram import Update
from telegram.ext import ContextTypes


async def send_error(e_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    errors = {
        "symbol": "Please enter a valid crypto symbol.",
        "generic": "An error occurred. Please try again later.",
        "erc_contract": "⚠️ invalid erc20 contract",
        "bsc_contract": "⚠️ invalid bsc contract",
    }
    cur_error = errors.get(e_type, "Generic error.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=cur_error)
