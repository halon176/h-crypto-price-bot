import logging

from telegram import Update
from telegram.ext import CallbackContext

from src.handlers.cg_calls import get_cg_chart, get_cg_price
from src.handlers.cmc_calls import get_cmc_price
from src.utils.shared import chart_template
from src.utils.bot import send_tg
from src.utils.errors import send_error


async def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_option = query.data

    if selected_option.startswith("chart_"):
        await get_cg_chart(selected_option[6:], update, context)
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    elif selected_option.startswith("cmc_"):
        coin_id = selected_option[4:]
        await get_cmc_price(coin_id, update, context)
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    elif selected_option.startswith("charttemplate_"):
        chart_template.set_template(selected_option[14:])
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

        await send_tg(context, update.effective_chat.id, f"{selected_option[21:]} theme selected")

    elif selected_option.startswith("period_"):
        indexdot = selected_option.index(".")
        await get_cg_chart(
            selected_option[indexdot + 1 :],
            update,
            context,
            selected_option[7:indexdot],
        )
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    else:
        try:
            await get_cg_price(selected_option, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await send_error("generic", update, context)

        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
