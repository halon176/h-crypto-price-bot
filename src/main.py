import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from cg_calls import get_coin_list, get_cg_price, get_api_id
from config import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot initialized")


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coin_list
    if not coin_list:
        coin_list = await get_coin_list()

    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid crypto symbol.")
        return

    crypto_symbol = context.args[0]

    coins = await get_api_id(crypto_symbol, coin_list)
    if coins == "symbol_error":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid crypto symbol.")
        return
    await get_cg_price(coins[0], update, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    crypto_price_handler = CommandHandler('p', cg_price_handler)
    application.add_handler(crypto_price_handler)

    application.run_polling()
