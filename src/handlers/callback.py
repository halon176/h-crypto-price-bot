"""Callback query handler for inline keyboard interactions."""

import logging

import logfire
from opentelemetry import context as otel_context
from opentelemetry import propagate as otel_propagate
from opentelemetry import trace as otel_trace
from telegram import Update
from telegram.ext import CallbackContext

from src.constants import CallbackPrefix
from src.handlers.cg_calls import get_cg_chart, get_cg_price
from src.handlers.cmc_calls import get_cmc_price
from src.models import CallbackData
from src.utils.bot import send_tg
from src.utils.errors import send_error
from src.utils.shared import chart_template


async def _delete_message(context: CallbackContext, chat_id: int, message_id: int) -> None:
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.warning(f"Failed to delete message {message_id}: {e}")


def _build_span_name(callback_data: CallbackData) -> str:
    match callback_data.prefix:
        case CallbackPrefix.CG:
            return f"cg_price {callback_data.value}"
        case CallbackPrefix.CMC:
            return f"cmc_price {callback_data.value}"
        case CallbackPrefix.CHART:
            return f"cg_chart {callback_data.value}"
        case CallbackPrefix.PERIOD:
            return f"cg_chart_period {callback_data.action} {callback_data.value}"
        case CallbackPrefix.THEME:
            return f"chart_theme {callback_data.action}"
        case _:
            return "callback_handler"


async def callback_handler(update: Update, context: CallbackContext) -> None:
    # Restore parent trace context (stored during disambiguation or chart display)
    # so this span becomes a child of the original command span.
    carrier = context.user_data.pop("_trace_carrier", {})
    token = otel_context.attach(otel_propagate.extract(carrier))

    try:
        query = update.callback_query
        if not query or not query.data:
            logging.warning("Received callback without query data")
            return

        callback_string = query.data
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        try:
            callback_data = CallbackData.parse(callback_string)
        except ValueError as e:
            logging.error(f"Invalid callback data format: {callback_string} - {e}")
            await send_error("generic", update, context)
            return

        with logfire.span(_build_span_name(callback_data)):
            span = otel_trace.get_current_span()
            span.set_attribute("chat.id", str(chat_id))
            span.set_attribute("user.id", str(update.effective_user.id))

            try:
                match callback_data.prefix:
                    case CallbackPrefix.CG:
                        span.set_attribute("coin.id", callback_data.value)
                        await get_cg_price(callback_data.value, update, context)
                    case CallbackPrefix.CMC:
                        span.set_attribute("coin.id", callback_data.value)
                        await get_cmc_price(int(callback_data.value), update, context)
                    case CallbackPrefix.CHART:
                        span.set_attribute("coin.id", callback_data.value)
                        await get_cg_chart(callback_data.value, update, context)
                    case CallbackPrefix.THEME:
                        span.set_attribute("chart.theme", callback_data.action)
                        chart_template.set_template(callback_data.action)
                        await send_tg(context, update.effective_chat.id, f"{callback_data.action} theme selected")
                    case CallbackPrefix.PERIOD:
                        span.set_attribute("coin.id", callback_data.value)
                        span.set_attribute("chart.period_days", callback_data.action)
                        await get_cg_chart(callback_data.value, update, context, callback_data.action)
                    case _:
                        logging.warning(f"Unknown callback prefix: {callback_data.prefix!r} in {callback_string!r}")
            except Exception as e:
                span.record_exception(e)
                logging.error(f"Error processing callback {callback_string}: {e}")
                await send_error("generic", update, context)
            finally:
                await _delete_message(context, chat_id, message_id)
    finally:
        otel_context.detach(token)
