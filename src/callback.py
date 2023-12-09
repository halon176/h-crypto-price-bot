import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
)

from src.cg_calls import get_cg_price, get_cg_chart
from src.cmc_calls import get_cmc_price
from src.shared import ChartTemplate

chart_template = ChartTemplate()


async def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_option = query.data

    if selected_option.startswith("chart_"):
        await get_cg_chart(selected_option[6:], update, context)
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )
    elif selected_option.startswith("cmc_"):
        coin_id = selected_option[4:]
        await get_cmc_price(coin_id, update, context)
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )

    elif selected_option.startswith("charttemplate_"):
        chart_template.set_template(selected_option[14:])
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{selected_option[21:]} theme selected",
        )

    elif selected_option.startswith("period_"):
        indexdot = selected_option.index(".")
        await get_cg_chart(
            selected_option[indexdot + 1 :],
            update,
            context,
            selected_option[7:indexdot],
        )
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )

    else:
        try:
            await get_cg_price(selected_option, update, context)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later.",
            )
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )
