import logging
from functools import reduce

import logfire
from opentelemetry import trace as otel_trace
from opentelemetry.trace import StatusCode
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings as s
from src.constants import ETHERSCAN_API_BASE, GAS_LIMIT_STANDARD_TRANSFER, GWEI_TO_ETH
from src.utils.bot import send_tg
from src.utils.errors import send_error
from src.utils.formatters import human_format, max_column_size
from src.utils.http import fetch_url


async def _etherscan_result(module: str, action: str) -> dict | None:
    """Return the `result` of an Etherscan V2 call on Ethereum mainnet, or None if the call failed."""
    response = await fetch_url(
        f"{ETHERSCAN_API_BASE}?chainid=1&module={module}&action={action}&apikey={s.ETHSCAN_API_KEY.get_secret_value()}",
        service="etherscan",
    )
    if not response or response.get("status") != "1":
        # Etherscan reports errors (invalid key, rate limit, ...) with HTTP 200, status "0" and the reason in `result`.
        logging.error(f"Etherscan {module}/{action} failed: {response.get('result') if response else 'no response'}")
        return None
    return response["result"]


@logfire.instrument("gas_handler")
async def gas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    span = otel_trace.get_current_span()
    span.set_attribute("chat.id", str(update.effective_chat.id))
    span.set_attribute("user.id", str(update.effective_user.id))
    if not s.ETHSCAN_API_KEY:
        await send_tg(context, update.effective_chat.id, "The bot has been launched without an Etherscan API KEY.")
        return

    gas_result = await _etherscan_result("gastracker", "gasoracle")
    logging.info("Request etherscan gas price")
    eth_price_result = await _etherscan_result("stats", "ethprice") if gas_result else None

    if not gas_result or not eth_price_result:
        span.set_status(StatusCode.ERROR, "Etherscan request failed")
        await send_error("generic", update, context)
        return

    eth_price = float(eth_price_result["ethusd"])
    mood_emoji = ["😎", "😄", "🤨", "😰", "💀"]
    gas_data = {
        "Safe": "SafeGasPrice",
        "Fast": "FastGasPrice",
        "Suggested": "suggestBaseFee",
    }

    class GasEntry:
        def __init__(self, gas_entry, entry_price) -> None:
            self.gas_entry = gas_entry
            # Gas is often below 1 gwei: keep significant digits instead of a fixed number of decimals.
            self.price_entry = human_format(float(entry_price))
            self.emoji = self.assign_emoji(entry_price)
            self.usd_value = f"{human_format(self.estimate_function_cost(entry_price))}$"

        @staticmethod
        def assign_emoji(entry_price) -> str:
            price = float(entry_price)
            if price < 20:
                return mood_emoji[0]
            elif 50 > price >= 20:
                return mood_emoji[1]
            elif 75 > price >= 50:
                return mood_emoji[2]
            elif 100 > price >= 75:
                return mood_emoji[3]
            elif price >= 100:
                return mood_emoji[4]

        @staticmethod
        def estimate_function_cost(gwei_value) -> float:
            cost_in_eth = GAS_LIMIT_STANDARD_TRANSFER * float(gwei_value) / GWEI_TO_ETH
            return cost_in_eth * eth_price

    span.set_attribute("eth.price_usd", eth_price)
    span.set_attribute("eth.gas.safe_gwei", float(gas_result["SafeGasPrice"]))
    span.set_attribute("eth.gas.fast_gwei", float(gas_result["FastGasPrice"]))
    span.set_attribute("eth.gas.suggested_base_fee_gwei", float(gas_result["suggestBaseFee"]))

    gas_price = []
    for label, data_key in gas_data.items():
        gas_price.append(GasEntry(label, gas_result[data_key]))

    gp_column_size = [
        2,
        max_column_size([gp.gas_entry for gp in gas_price]),
        max_column_size([gp.price_entry for gp in gas_price]),
        max_column_size([gp.usd_value for gp in gas_price]),
    ]

    str_format_gp = f"{{}} {{:{gp_column_size[1]}}}  {{:>{gp_column_size[2]}}}  {{:>{gp_column_size[3]}}}"

    gas_price_header = [
        "```",
        "-" * (len(gp_column_size) + 1 + reduce(lambda a, b: a + b, gp_column_size)),
    ]
    message = "\n".join(
        ["⛽ Ethereum Gas Fee"]
        + gas_price_header
        + [str_format_gp.format(gp.emoji, gp.gas_entry, gp.price_entry, gp.usd_value) for gp in gas_price]
        + list(reversed(gas_price_header))
    )

    await send_tg(context, update.effective_chat.id, message)
