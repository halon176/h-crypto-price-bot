import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from cg_calls import get_cg_price, get_api_id, get_cg_dominance, get_coin_list
from config import TOKEN
from news import news

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = []
coin_list_update = datetime.datetime.now()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="markdown",
        text="Hi! I am HCryptoPrice, You can ask me for the current price of any crypto by typing:\n\n"
             "`/p <crypto_symbol>` \n\n"
             "For example, `/p btc` will give you the current price of Bitcoin. Enjoy!\n\n"
             "To display the complete list of commands, type `/help`"
    )
    logging.info(f'Start call')


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="markdown",
        disable_web_page_preview=True,
        text="📚*List of Commands:*\n\n"
             "`/p <crypto_symbol>` - to receive the current price and historical variation of the coin \n"
             "`/dom` - to receive the top 10 most capitalized tokens \n"
             "`/news` - to receive CoinTelegraph news \n"
             "`/help` - to receive this message\n\n"
             "This bot is written with open-source and free code, and you can find it all at "
             "[GitHub](https://github.com/halon176/h-crypto-price-bot)"
    )
    logging.info(f'Help call')


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


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coin_list, coin_list_update
    if not coin_list:
        coin_list = await get_coin_list()

    if len(context.args) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter a valid crypto symbol."
        )
        return

    crypto_symbol = context.args[0].lower()
    coins = await get_api_id(crypto_symbol, coin_list)
    if not coins:
        if (datetime.datetime.now() - coin_list_update) >= datetime.timedelta(hours=1):
            coin_list = await get_coin_list()
            coin_list_update = datetime.datetime.now()
            logging.info("Reloaded coin list")
            coins = await get_api_id(crypto_symbol, coin_list)
            if not coins:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Please enter a valid crypto symbol."
                )
                return
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter a valid crypto symbol."
            )
            return

    if len(coins) == 1:
        try:
            await get_cg_price(coins[0], update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later."
            )
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

    crypto_dominance_handler = CommandHandler('dom', get_cg_dominance)
    application.add_handler(crypto_dominance_handler)

    news_handler = CommandHandler('news', news)
    application.add_handler(news_handler)

    help_handler = CommandHandler('help', bot_help)
    application.add_handler(help_handler)

    menu_handler = CallbackQueryHandler(menu_handler)
    application.add_handler(menu_handler)

    application.run_polling()
