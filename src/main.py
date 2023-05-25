import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

from callback import callback_handler
from cg_calls import get_cg_price, get_api_id, get_cg_dominance, get_cg_chart
from cmc_calls import ogz_price
from config import TELEGRAM_TOKEN
from defilama_calls import get_defilama_price
from ethersca_calls import gas_handler
from info import start, bot_help
from news import news
from shared import ChartTemplate, CoinList

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

coin_list = CoinList()
coin_list.update()

chart_template = ChartTemplate()


async def coin_check(coin, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    coin_type = kwargs.get('type', None)
    if len(coin) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter a valid crypto symbol."
        )
        return False
    coins = await get_api_id(coin)
    if not coins:
        coin_list.update()
        coins = await get_api_id(coin)
        if not coins:
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


async def eth_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args[0]) == 42 and context.args[0].startswith('0x'):
        await get_defilama_price(context.args[0], 'ethereum', update, context)
    else:
        error_message = '⚠️ invalid erc20 contract'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)


async def bsc_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args[0]) == 42 and context.args[0].startswith('0x'):
        await get_defilama_price(context.args[0], 'bsc', update, context)
    else:
        error_message = '⚠️ invalid bsc contract'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    price_handler = CommandHandler('p', cg_price_handler)
    application.add_handler(price_handler)

    chart_handler = CommandHandler('c', cg_chart_handler)
    application.add_handler(chart_handler)

    eth_contract_handler_b = CommandHandler('eth', eth_contract_handler)
    application.add_handler(eth_contract_handler_b)

    bsc_contract_handler_b = CommandHandler('bsc', bsc_contract_handler)
    application.add_handler(bsc_contract_handler_b)

    chart_color = CommandHandler('chart_color', chart_color_handler)
    application.add_handler(chart_color)

    ogz_price_handler = CommandHandler('ogz', ogz_price)
    application.add_handler(ogz_price_handler)

    crypto_gas_handler = CommandHandler('gas', gas_handler)
    application.add_handler(crypto_gas_handler)

    crypto_dominance_handler = CommandHandler('dom', get_cg_dominance)
    application.add_handler(crypto_dominance_handler)

    news_handler = CommandHandler('news', news)
    application.add_handler(news_handler)

    help_handler = CommandHandler('help', bot_help)
    application.add_handler(help_handler)

    menu_handler = CallbackQueryHandler(callback_handler)
    application.add_handler(menu_handler)

    application.run_polling()
