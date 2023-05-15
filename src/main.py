import datetime
import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from cg_calls import get_cg_price, get_api_id, get_cg_dominance, get_coin_list, get_cg_chart
from config import TELEGRAM_TOKEN
from ethersca_calls import gas_handler
from info import start, bot_help
from news import news

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = []
coin_list_update = datetime.datetime.now()


async def coin_check(coin, update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coin_list, coin_list_update
    if not coin_list:
        coin_list = await get_coin_list()

    if len(coin) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter a valid crypto symbol."
        )
        return False
    coins = await get_api_id(coin, coin_list)
    if not coins:
        if (datetime.datetime.now() - coin_list_update) >= datetime.timedelta(hours=1):
            coin_list = await get_coin_list()
            coin_list_update = datetime.datetime.now()
            logging.info("Reloaded coin list")
            coins = await get_api_id(coin, coin_list)
            if not coins:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Please enter a valid crypto symbol."
                )
                return False
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter a valid crypto symbol."
            )
            return False

    if len(coins) == 1:
        return coins[0]
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


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto_symbol = context.args[0].lower()
    coin = await coin_check(crypto_symbol, update, context)
    if coin:
        try:
            await get_cg_price(coin, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later."
            )


async def callback_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    selected_option = query.data
    if selected_option.startswith("period_"):
        print(selected_option)
    else:
        try:
            await get_cg_price(selected_option, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later."
            )
        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )


async def cg_chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto_symbol = context.args[0].lower()
    coins = await get_api_id(crypto_symbol, coin_list)
    await get_cg_chart(coins[0], "30")

    keyboard = [
        [InlineKeyboardButton("24h", callback_data='period_1'),
         InlineKeyboardButton("7d", callback_data='period_7'),
         InlineKeyboardButton("✅ 30d", callback_data='period_30'),
         InlineKeyboardButton("90d", callback_data='period_90'),
         InlineKeyboardButton("1y", callback_data='period_365'),
         InlineKeyboardButton("max", callback_data='period_max')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=open('plot.jpg', 'rb'),
                                 reply_markup=reply_markup)
    os.remove('plot.jpg')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    price_handler = CommandHandler('p', cg_price_handler)
    application.add_handler(price_handler)

    chart_handler = CommandHandler('c', cg_chart_handler)
    application.add_handler(chart_handler)

    crypto_gas_handler = CommandHandler('gas', gas_handler)
    application.add_handler(crypto_gas_handler)

    crypto_dominance_handler = CommandHandler('dom', get_cg_dominance)
    application.add_handler(crypto_dominance_handler)

    news_handler = CommandHandler('news', news)
    application.add_handler(news_handler)

    help_handler = CommandHandler('help', bot_help)
    application.add_handler(help_handler)

    menu_handler = CallbackQueryHandler(callback_menu_handler)
    application.add_handler(menu_handler)

    application.run_polling()
