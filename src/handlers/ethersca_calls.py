import logging
from functools import reduce

from telegram import Update
from telegram.ext import ContextTypes
from web3 import Web3

from src.config import settings as s
from src.utils.formatters import max_column_size
from src.utils.http import fetch_url
from src.utils.bot import send_tg



async def gas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    eth_scan_api_error = "The bot has been launched without an Etherscan API KEY."
    if not s.ETHSCAN_API_KEY:
        await send_tg(context, update.effective_chat.id, eth_scan_api_error)
        return

    gas_request = await fetch_url(
        f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={s.ETHSCAN_API_KEY.get_secret_value()}"
    )
    logging.info("Request etherscan gas price")

    if gas_request["status"] == "0":
        await send_tg(context, update.effective_chat.id, eth_scan_api_error)
        return

    if gas_request["status"] == "1":
        mood_emoji = ["😎", "😄", "🤨", "😰", "💀"]
        gas_data = {
            "Safe": "SafeGasPrice",
            "Fast": "FastGasPrice",
            "Suggested": "suggestBaseFee",
        }

        async def get_eth_price() -> float:
            response = await fetch_url(
                f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={s.ETHSCAN_API_KEY.get_secret_value()}"
            )
            price = float(response["result"]["ethusd"])
            return price

        eth_price = await get_eth_price()

        class GasEntry:
            def __init__(self, gas_entry, entry_price) -> None:
                self.gas_entry = gas_entry
                self.price_entry = f"{float(entry_price):.1f}"
                self.emoji = self.assign_emoji(entry_price)
                self.usd_value = f"{float(self.estimate_function_cost(entry_price)):.2f}$"

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
                gas_limit = 21000
                wei_value = Web3.to_wei(gwei_value, "gwei")
                cost_in_eth = Web3.from_wei(gas_limit * wei_value, "ether")
                cost_in_eth = float(cost_in_eth)
                cost_in_usd = cost_in_eth * eth_price
                return cost_in_usd

        gas_result = gas_request["result"]

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
