import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from cg_calls import get_coin_list, get_cg_price, get_api_id
from config import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="markdown",
        text="Hi! I am HCryptoPrice, You can ask me for the current price of any crypto by typing:\n\n"
             "`/p <crypto_symbol>` \n\n"
             "For example, `/p btc` will give you the current price of Bitcoin. Enjoy!"
    )


async def callback(update, context):
    query = update.callback_query
    print(query)

    selected_option = query.data

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="You selected " + selected_option
    )


async def menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    selected_option = query.data
    await get_cg_price(selected_option, update, context)
    await context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coin_list
    if not coin_list:
        coin_list = await get_coin_list()

    if len(context.args) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter a valid crypto symbol."
        )
        return

    crypto_symbol = context.args[0]

    coins = await get_api_id(crypto_symbol, coin_list)
    if coins == "symbol_error":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter a valid crypto symbol."
        )
        return
    coins = [coin for coin in coins if "-peg-" not in coin]
    if len(coins) == 1:
        await get_cg_price(coins[0], update, context)
    else:
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data=crypto)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🟠 There are multiple coins with the same symbol, please select the desired one:",
            reply_markup=reply_markup
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    crypto_price_handler = CommandHandler('p', cg_price_handler)
    application.add_handler(crypto_price_handler)

    menu_handler = CallbackQueryHandler(menu_handler)
    application.add_handler(menu_handler)

    application.run_polling()
