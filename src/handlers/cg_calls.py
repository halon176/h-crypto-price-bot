"""CoinGecko API handlers for cryptocurrency data."""

import io
import logging
from functools import reduce

import pandas as pd
import plotly.express as px
import plotly.io as pio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.constants import (
    COINGECKO_API_COINS,
    COINGECKO_API_GLOBAL,
    MESSAGE_RATE_LIMIT_EXCEEDED,
    POSITIONAL_EMOJIS,
)
from src.models import AtEntry, GeneralDataEntry, MarketCapEntry, PriceChangeEntry
from src.utils.bot import send_tg
from src.utils.errors import send_error
from src.utils.formatters import (
    human_format,
    max_column_size,
)
from src.utils.http import fetch_url, write_call
from src.utils.shared import cg_coin_list, chart_template

logger = logging.getLogger(__name__)


def get_cg_id(crypto_symbol: str) -> list[str]:
    """Get CoinGecko IDs for a given cryptocurrency symbol.

    Args:
        crypto_symbol: Cryptocurrency symbol (e.g., 'btc', 'eth')

    Returns:
        List of matching CoinGecko IDs
    """
    api_ids = []
    for crypto in cg_coin_list.coin_list:
        if crypto["symbol"] == crypto_symbol:
            api_ids.append(crypto["id"])
    return api_ids


async def get_cg_coin_info(coin_id: str) -> dict[str, str] | None:
    """Get coin information from CoinGecko coin list.

    Args:
        coin_id: CoinGecko coin ID

    Returns:
        Dictionary with 'name' and 'symbol', or None if not found
    """
    for crypto in cg_coin_list.coin_list:
        if coin_id == crypto["id"]:
            return {"name": crypto["name"], "symbol": crypto["symbol"].upper()}
    return None


async def get_cg_price(coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display detailed price information for a cryptocurrency.

    Args:
        coin: CoinGecko coin ID
        update: Telegram update object
        context: Telegram context
    """
    url_params = (
        "?localization=false&tickers=false&market_data=true&"
        "community_data=false&developer_data=false&sparkline=false"
    )

    # Check rate limiting
    rate_limit_ok = await write_call(1, 1, str(update.effective_chat.id), coin)
    if not rate_limit_ok:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=MESSAGE_RATE_LIMIT_EXCEEDED,
        )
        return

    url = COINGECKO_API_COINS + coin + url_params
    logger.info(f"Fetching CoinGecko price data: {url}")

    crypto_data = await fetch_url(url)

    if not crypto_data:
        await send_error("generic", update, context)
        return

    if len(crypto_data) == 0:
        await send_error("symbol", update, context)
        return

    # Extract basic info
    market_cap_rank = (
        f"{crypto_data['market_cap_rank']}°"
        if crypto_data.get("market_cap_rank")
        else ""
    )
    crypto_name = crypto_data["name"]
    usd_price = crypto_data["market_data"]["current_price"].get("usd")
    crypto_price = human_format(usd_price) if usd_price is not None else "N/A"

    # Clean homepage URL (remove query parameters)
    homepage = crypto_data["links"]["homepage"][0]
    try:
        query_index = homepage.index("?")
        web = homepage[:query_index]
    except ValueError:
        web = homepage

    twitter = f"https://twitter.com/{crypto_data['links']['twitter_screen_name']}"
    symbol = crypto_data["symbol"].upper()

    # Price change data configuration
    price_change_config = {
        "24h": "price_change_percentage_24h",
        "7d": "price_change_percentage_7d",
        "14d": "price_change_percentage_14d",
        "30d": "price_change_percentage_30d",
        "60d": "price_change_percentage_60d",
        "200d": "price_change_percentage_200d",
        "1y": "price_change_percentage_1y",
    }

    # General data schema
    general_data_schema = (
        ("💰", "M. Cap", "market_cap"),
        ("💵", "Circ. S", "circulating_supply"),
        ("🖨", "Total S", "total_supply"),
    )

    # Build general data entries
    general_data = []
    for emoji, label, data_key in general_data_schema:
        if data_key == "market_cap":
            value = crypto_data["market_data"].get(data_key, {}).get("usd", "N/A")
        else:
            value = crypto_data["market_data"].get(data_key, "N/A")
        general_data.append(GeneralDataEntry(emoji, label, value))

    # Format general data table
    column_sizes_general = [
        2,
        max_column_size([item.entry for item in general_data]),
        max_column_size([item.value for item in general_data]),
    ]

    format_general = f"{{}} {{:{column_sizes_general[1]}}}   {{:>{column_sizes_general[2]}}}"
    general_data_message = "\n".join(
        [format_general.format(item.emoji, item.entry, item.value) for item in general_data]
    )

    # Build price change entries
    price_changes = []
    for label, data_key in price_change_config.items():
        value = crypto_data["market_data"].get(data_key)
        price_changes.append(PriceChangeEntry(label, value))

    # Format price changes table
    column_sizes_changes = [
        max_column_size([pc.entry for pc in price_changes]),
        max_column_size([pc.percentage for pc in price_changes]),
    ]

    format_price_change = f"{{:{column_sizes_changes[0]}}}    {{:>{column_sizes_changes[1]}}}"
    price_change_message = "\n".join(
        [format_price_change.format(pc.entry, pc.percentage) for pc in price_changes]
    )

    # All-time high/low data schema
    at_data_schema = (
        ("📈", "ATH", "ath", "ath_change_percentage", "ath_date"),
        ("📉", "ATL", "atl", "atl_change_percentage", "atl_date"),
    )

    # Build ATH/ATL entries
    at_data = []
    for emoji, label, price_key, percentage_key, date_key in at_data_schema:
        at_price = crypto_data["market_data"][price_key]
        at_percentage = crypto_data["market_data"][percentage_key]
        at_date = crypto_data["market_data"][date_key]
        at_data.append(AtEntry(emoji, label, at_price, at_percentage, at_date))

    # Format ATH/ATL table
    column_sizes_at = [
        2,
        max_column_size([at.symbol for at in at_data]),
        max_column_size([at.price for at in at_data]),
        max_column_size([at.percentage for at in at_data]),
        max_column_size([at.date for at in at_data]),
    ]

    format_at = (
        f"{{:{column_sizes_at[0]}}}{{:{column_sizes_at[1]}}} {{:>{column_sizes_at[2]}}}"
        f" ({{:>{column_sizes_at[3]}}}) {{:>{column_sizes_at[4]}}}"
    )

    at_data_message = "\n".join(
        [format_at.format(at.emoji, at.symbol, at.price, at.percentage, at.date) for at in at_data]
    )

    # Create separator line
    separator = (
        "-" * (len(column_sizes_changes) + 2 + reduce(lambda a, b: a + b, column_sizes_changes)) + "\n"
    )

    # Build final message
    message = (
        f"{market_cap_rank} [{crypto_name}]({web}) [{symbol}]({twitter})\n"
        f"`Price: {crypto_price}$`\n"
        f"`{separator}`"
        f"`{price_change_message}`\n"
        f"`{separator}`"
        f"`{general_data_message}`\n"
        f"`{at_data_message}`"
    )

    await send_tg(context, update.effective_chat.id, message, mk_parse=False)


async def get_cg_chart(coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE, period="30") -> None:
    r = await write_call(1, 2, str(update.effective_chat.id), coin)
    if not r:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=MESSAGE_RATE_LIMIT_EXCEEDED,
        )
        return
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={period}"
    chart = await fetch_url(url)
    if not chart:
        await send_error("generic", update, context)
        return
    logging.info(f"Request URL: {url}")
    x = [p[0] / 1000 for p in chart["prices"]]
    y = [p[1] for p in chart["prices"]]

    df = pd.DataFrame({"timeframe": x, "prices": y})
    df["timeframe"] = pd.to_datetime(df["timeframe"], unit="s")
    info = await get_cg_coin_info(coin)
    title = f"{info['name']} ({info['symbol']})"
    bottom = f"{period} day{'s' if period != '1' else ''} chart"
    template = chart_template.get_template()
    fig = px.line(
        df,
        x="timeframe",
        y="prices",
        template=template,
        labels={"timeframe": bottom, "prices": "price ($)"},
    )

    fig.update_layout(title={"text": title, "y": 0.93, "x": 0.5, "font": {"size": 24}})

    buffer = io.BytesIO()
    pio.write_image(fig, buffer, format="jpg")
    buffer.seek(0)

    periods = [
        {"1": "24h"},
        {"7": "7d"},
        {"30": "30d"},
        {"90": "90d"},
        {"365": "1y"},
        # {"max": "max"},
    ]
    checkbox = [""] * 6

    for i in range(len(periods)):
        current_key = list(periods[i].keys())[0]
        if period == current_key:
            checkbox[i] = "✅"

    keyboard = [
        [
            InlineKeyboardButton(
                f"{checkbox[i]}{list(periods[i].values())[0]}",
                callback_data=f"period_{list(periods[i].keys())[0]}.{coin}",
            )
            for i in range(len(periods))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_tg(context, update.effective_chat.id, photo=buffer, reply_markup=reply_markup)

    buffer.close()


async def get_cg_dominance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display cryptocurrency market dominance rankings.

    Args:
        update: Telegram update object
        context: Telegram context
    """
    global_data = await fetch_url(COINGECKO_API_GLOBAL)
    if not global_data:
        await send_error("generic", update, context)
        return

    logger.info("Fetching coin dominance rankings")

    dom_percentage = list(global_data["data"]["market_cap_percentage"].items())
    market_cap_entries = [MarketCapEntry.from_tuple(item) for item in dom_percentage]

    column_sizes = [
        2,
        max_column_size([entry.symbol for entry in market_cap_entries]),
        max_column_size([entry.percentage for entry in market_cap_entries]),
    ]

    separator = "-" * (len(column_sizes) + reduce(lambda a, b: a + b, column_sizes))
    header = ["```", separator]

    format_string = f"{{}}  {{:{column_sizes[1]}}} {{:>{column_sizes[2]}}}"
    message = "\n".join(
        [f"🏆 TOP {len(market_cap_entries)} MARKETCAP 🏆"]
        + header
        + [
            format_string.format(emoji, entry.symbol, entry.percentage)
            for emoji, entry in zip(POSITIONAL_EMOJIS, market_cap_entries, strict=False)
        ]
        + list(reversed(header))
    )

    await send_tg(context, update.effective_chat.id, message)


async def chart_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    themes = [
        ["🌕 white", "charttemplate_plotly_white"],
        ["🌑 dark", "charttemplate_plotly_dark"],
    ]
    keyboard = []
    for theme in themes:
        button = [InlineKeyboardButton(theme[0], callback_data=theme[1])]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_tg(context, update.effective_chat.id, text="🟠 select desired chart theme", reply_markup=reply_markup)


async def gc_coin_check(
    coin: str, update: Update, context: ContextTypes.DEFAULT_TYPE, call_type: str = "price"
) -> str | None:
    if not coin:
        await send_error("symbol", update, context)
        return None

    coins = get_cg_id(coin)

    if not coins:
        await cg_coin_list.update()
        coins = get_cg_id(coin)
        if not coins:
            await send_error("symbol", update, context)
            return None

    text = "🟠 There are multiple coins with the same symbol, please select the desired one:"

    if len(coins) == 1:
        return coins[0]
    elif call_type == "chart":
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data=f"chart.{crypto}")]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)

        await send_tg(context, update.effective_chat.id, text, reply_markup=reply_markup)
    else:
        keyboard = []
        for crypto in coins:
            button = [InlineKeyboardButton(crypto, callback_data=crypto)]
            keyboard.append(button)
        reply_markup = InlineKeyboardMarkup(keyboard)

        await send_tg(context, update.effective_chat.id, text, reply_markup=reply_markup)


async def cg_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cgprice command to display cryptocurrency price.

    Args:
        update: Telegram update object
        context: Telegram context with args containing crypto symbol
    """
    if not context.args:
        await send_error("symbol", update, context)
        return

    crypto_symbol = context.args[0].lower()
    coin = await gc_coin_check(crypto_symbol, update, context)

    if coin:
        try:
            await get_cg_price(coin, update, context)
        except Exception as e:
            logger.error(f"Error fetching price for {crypto_symbol}: {e}", exc_info=True)
            await send_error("generic", update, context)


async def cg_chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cgchart command to display cryptocurrency chart.

    Args:
        update: Telegram update object
        context: Telegram context with args containing crypto symbol
    """
    if not context.args:
        await send_error("symbol", update, context)
        return

    crypto_symbol = context.args[0].lower()
    coin = await gc_coin_check(crypto_symbol, update, context, "chart")

    if coin:
        try:
            await get_cg_chart(coin, update, context)
        except Exception as e:
            logger.error(f"Error fetching chart for {crypto_symbol}: {e}", exc_info=True)
            await send_error("generic", update, context)
