import logging
from functools import reduce

import requests
from telegram import Update
from telegram.ext import ContextTypes

from config import ETHSCAN_API_KEY
from src.service import max_column_size


async def gas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_request = requests.get(
        f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHSCAN_API_KEY}").json()
    logging.info('Request etherscan gas price')

    if gas_request["status"] == "0":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="The bot has been launched without an Etherscan API KEY.")
    if gas_request["status"] == "1":
        mood_emoji = ["😎", "😄", "🤨", "😰", "💀"]
        gas_data = {
            "Safe Gas Price": "SafeGasPrice",
            "Fast Gas Price": "FastGasPrice",
            "Suggested Gas": "suggestBaseFee"
        }

        class GasEntry:
            def __init__(self, gas_entry, entry_price):

                self.gas_entry = gas_entry
                self.price_entry = f"{float(entry_price):.1f}"
                self.emoji = self.assign_emoji(entry_price)

            @staticmethod
            def assign_emoji(entry_price):
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

        gas_result = gas_request["result"]

        gas_price = []
        for label, data_key in gas_data.items():
            gas_price.append(GasEntry(label, gas_result[data_key]))

        gp_column_size = [
            2,
            max_column_size((gp.gas_entry for gp in gas_price)),
            max_column_size((gp.price_entry for gp in gas_price))
        ]

        str_format_gp = f"{{}} {{:{gp_column_size[1]}}}  {{:>{gp_column_size[2]}}}"

        gas_price_message = "\n".join(
            [str_format_gp.format(gp.emoji, gp.gas_entry, gp.price_entry) for gp in gas_price])

        gas_price_header = [
            "```",
            "-" * (len(gp_column_size) + reduce(lambda a, b: a + b, gp_column_size))
        ]
        message = "\n".join(
            ["⛽ Ethereum Gas in gwei"]
            + gas_price_header
            + [str_format_gp.format(gp.emoji, gp.gas_entry, gp.price_entry) for gp in gas_price]
            + list(reversed(gas_price_header))
        )

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=message,
                                       parse_mode="markdown",
                                       disable_web_page_preview=True)
