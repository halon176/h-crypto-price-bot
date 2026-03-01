"""Callback query handler for inline keyboard interactions."""

import logging

import logfire
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
        logging.error(f"Error handling callback for coin {coin_id}: {e}")
        await send_error("generic", update, context)


@logfire.instrument("callback_handler")
async def callback_handler(update: Update, context: CallbackContext) -> None:
    """Main callback query handler for inline keyboard interactions.

    Processes callback queries from inline keyboards and routes them to
    appropriate handlers based on the callback data prefix.

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
    query = update.callback_query
    if not query or not query.data:
        logging.warning("Received callback without query data")
        return

    callback_string = query.data
    chat_id = query.message.chat.id
    message_id = query.message.message_id

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
            await _handle_chart_callback(callback_data, update, context)
        elif prefix == "cmc":  # Keep as string for backward compatibility
            await _handle_cmc_callback(callback_data, update, context)
        elif prefix == "charttemplate" or prefix == CallbackPrefix.THEME.value:
            await _handle_theme_callback(callback_data, update, context)
        elif prefix == CallbackPrefix.PERIOD.value:
            await _handle_period_callback(callback_data, update, context)
        else:
            # Default: treat as coin_id
            await _handle_default_callback(callback_string, update, context)

    except ValueError as e:
        logging.error(f"Invalid callback data format: {callback_string} - {e}")
        await send_error("generic", update, context)
    except Exception as e:
        logging.error(f"Error processing callback {callback_string}: {e}")
        await send_error("generic", update, context)
    finally:
        # Always try to delete the message
        await _delete_message(context, chat_id, message_id)
