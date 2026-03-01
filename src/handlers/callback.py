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
    """Delete a message from the chat.

    Args:
        context: Telegram callback context
        chat_id: Chat ID
        message_id: Message ID to delete
    """
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.warning(f"Failed to delete message {message_id}: {e}")


async def _handle_chart_callback(
    callback_data: CallbackData,
    update: Update,
    context: CallbackContext
) -> None:
    """Handle chart-related callbacks.

    Args:
        callback_data: Parsed callback data
        update: Telegram update object
        context: Telegram callback context
    """
    await get_cg_chart(callback_data.value, update, context)


async def _handle_cmc_callback(
    callback_data: CallbackData,
    update: Update,
    context: CallbackContext
) -> None:
    """Handle CoinMarketCap price callbacks.

    Args:
        callback_data: Parsed callback data
        update: Telegram update object
        context: Telegram callback context
    """
    await get_cmc_price(callback_data.value, update, context)


async def _handle_theme_callback(
    callback_data: CallbackData,
    update: Update,
    context: CallbackContext
) -> None:
    """Handle chart theme selection callbacks.

    Args:
        callback_data: Parsed callback data
        update: Telegram update object
        context: Telegram callback context
    """
    theme = callback_data.action
    chart_template.set_template(theme)
    await send_tg(context, update.effective_chat.id, f"{theme} theme selected")


async def _handle_period_callback(
    callback_data: CallbackData,
    update: Update,
    context: CallbackContext
) -> None:
    """Handle chart period selection callbacks.

    Args:
        callback_data: Parsed callback data
        update: Telegram update object
        context: Telegram callback context
    """
    period = callback_data.action
    coin_id = callback_data.value
    await get_cg_chart(coin_id, update, context, period)


async def _handle_default_callback(
    coin_id: str,
    update: Update,
    context: CallbackContext
) -> None:
    """Handle default coin selection callbacks.

    Args:
        coin_id: Cryptocurrency ID
        update: Telegram update object
        context: Telegram callback context
    """
    try:
        await get_cg_price(coin_id, update, context)
    except Exception as e:
        otel_trace.get_current_span().record_exception(e)
        logging.error(f"Error handling callback for coin {coin_id}: {e}")
        await send_error("generic", update, context)


async def callback_handler(update: Update, context: CallbackContext) -> None:
    """Main callback query handler for inline keyboard interactions.

    Processes callback queries from inline keyboards and routes them to
    appropriate handlers based on the callback data prefix.

    If a disambiguation keyboard was shown (multiple coins for the same symbol),
    the trace context from the original command is restored so all spans share
    the same trace ID.

    Supported callback formats:
        - "chart.{coin_id}" - Display chart selection
        - "cmc.{coin_id}" - Get CoinMarketCap price
        - "theme_{theme}.{coin_id}" - Set chart theme
        - "period_{period}.{coin_id}" - Display chart for period
        - "{coin_id}" - Default: get CoinGecko price

    Args:
        update: Telegram update object containing the callback query
        context: Telegram callback context
    """
    # Restore parent trace context from the disambiguation step (if any),
    # so this span is a child of the original command span.
    carrier = context.user_data.pop("_trace_carrier", {})
    parent_ctx = otel_propagate.extract(carrier)
    token = otel_context.attach(parent_ctx)

    try:
        with logfire.span("callback_handler"):
            query = update.callback_query
            if not query or not query.data:
                logging.warning("Received callback without query data")
                return

            callback_string = query.data
            chat_id = query.message.chat.id
            message_id = query.message.message_id

            span = otel_trace.get_current_span()
            span.set_attribute("chat.id", str(chat_id))
            span.set_attribute("user.id", str(update.effective_user.id))

            try:
                # Parse callback data
                if "." in callback_string:
                    callback_data = CallbackData.parse(callback_string)
                    prefix = callback_data.prefix
                else:
                    # Default case: just coin_id
                    prefix = None
                    callback_data = None

                # Route to appropriate handler
                if prefix == CallbackPrefix.CHART.value:
                    span.set_attribute("callback.type", "chart")
                    span.set_attribute("coin.id", callback_data.value)
                    await _handle_chart_callback(callback_data, update, context)
                elif prefix == "cmc":  # Keep as string for backward compatibility
                    span.set_attribute("callback.type", "cmc_price")
                    span.set_attribute("coin.id", str(callback_data.value))
                    await _handle_cmc_callback(callback_data, update, context)
                elif prefix == "charttemplate" or prefix == CallbackPrefix.THEME.value:
                    span.set_attribute("callback.type", "chart_theme")
                    span.set_attribute("chart.theme", callback_data.action)
                    await _handle_theme_callback(callback_data, update, context)
                elif prefix == CallbackPrefix.PERIOD.value:
                    span.set_attribute("callback.type", "chart_period")
                    span.set_attribute("coin.id", callback_data.value)
                    span.set_attribute("chart.period_days", callback_data.action)
                    await _handle_period_callback(callback_data, update, context)
                else:
                    # Default: treat as coin_id (CG price disambiguation)
                    span.set_attribute("callback.type", "cg_price")
                    span.set_attribute("coin.id", callback_string)
                    await _handle_default_callback(callback_string, update, context)

            except ValueError as e:
                span.record_exception(e)
                logging.error(f"Invalid callback data format: {callback_string} - {e}")
                await send_error("generic", update, context)
            except Exception as e:
                span.record_exception(e)
                logging.error(f"Error processing callback {callback_string}: {e}")
                await send_error("generic", update, context)
            finally:
                # Always try to delete the message
                await _delete_message(context, chat_id, message_id)
    finally:
        otel_context.detach(token)
