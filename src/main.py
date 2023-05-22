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

from cg_calls import get_cg_price, get_api_id, get_cg_dominance, get_coin_list, get_cg_chart
from config import TELEGRAM_TOKEN
from ethersca_calls import gas_handler
from info import start, bot_help
from news import news
from src.shared import ChartTemplate

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = []
coin_last_update = datetime.datetime.now()

chart_template = ChartTemplate()


async def coin_check(coin, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    coin_type = kwargs.get('type', None)
    global coin_list, coin_last_update
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
        if (datetime.datetime.now() - coin_last_update) >= datetime.timedelta(hours=1):
            coin_list = await get_coin_list()
            coin_last_update = datetime.datetime.now()
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
    elif coin_type == 'chart':
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data="chart_" + crypto)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🟠 There are multiple coins with the same symbol, please select the desired one:",
            reply_markup=reply_markup
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

    if selected_option.startswith("chart_"):
        await get_cg_chart(selected_option[6:], update, context)
        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    elif selected_option.startswith("charttemplate_"):
        chart_template.set_template(selected_option[14:])
        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{selected_option[21:]} theme selected"
        )

    elif selected_option.startswith("period_"):
        indexdot = selected_option.index('.')
        await get_cg_chart(selected_option[indexdot + 1:], update, context, selected_option[7:indexdot])
        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

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
    coin = await coin_check(crypto_symbol, update, context, type='chart')
    if coin:
        await get_cg_chart(coin, update, context)


async def chart_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    themes = [['🌕 white', 'charttemplate_plotly_white'],
              ['🌑 dark', 'charttemplate_plotly_dark']]
    keyboard = []
    for theme in themes:
        button = [InlineKeyboardButton(theme[0], callback_data=theme[1])]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="🟠 select desired chart theme",
        reply_markup=reply_markup
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    price_handler = CommandHandler('p', cg_price_handler)
    application.add_handler(price_handler)

    chart_handler = CommandHandler('c', cg_chart_handler)
    application.add_handler(chart_handler)

    chart_color = CommandHandler('chart_color', chart_color_handler)
    application.add_handler(chart_color)

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
