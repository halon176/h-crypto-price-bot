import datetime
import logging

import httpx

from src.config import settings as s
from src.utils.formatters import format_date, human_format


class CoinList:
    _instance = None

    def __new__(cls) -> None:
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.coin_list: list[dict] | None = None
        self.coin_last_update = datetime.datetime(2023, 1, 1)


class CMCCoinList(CoinList):
    """
    Singleton class to store the CoinMarketCap coin list
    """

    def update(self, CMC_PRO_API_KEY: str | None = None) -> None:
        if CMC_PRO_API_KEY is None:
            return
        if (datetime.datetime.now() - self.coin_last_update) >= datetime.timedelta(hours=1):
            coin_request = httpx.get(
                "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
                headers={"X-CMC_PRO_API_KEY": s.CMC_API_KEY.get_secret_value()},
            )
            coin_list_gc = coin_request.json()
            self.coin_list = coin_list_gc
            self.coin_last_update = datetime.datetime.now()
            logging.info("Reloaded coin list from CoinMarketCap API")


class CGCoinList(CoinList):
    def update(self) -> None:
        if (datetime.datetime.now() - self.coin_last_update) >= datetime.timedelta(hours=1):
            coin_request = httpx.get("https://api.coingecko.com/api/v3/coins/list?include_platform=false")
            if coin_request.status_code != 200:
                e = (
                    f"Failed to fetch CoinGecko coin list, status code: {coin_request.status_code},"
                    f" probably temporary banned for too many requests, try again later"
                )
                logging.error(e)
                return
            self.coin_list = coin_request.json()
            self.coin_last_update = datetime.datetime.now()
            excluded_values = {
                "-peg-",
                "-wormhole",
                "wrapped",
                "oec-",
                "-iou",
                "harrypotter",
                "blackrocktradingcurrency",
            }
            self.coin_list = [
                crypto for crypto in self.coin_list if all(excluded not in crypto["id"] for excluded in excluded_values)
            ]
            logging.info("Reloaded coin list from CoinGecko API")


class ChartTemplate:
    _instance = None

    def __new__(cls) -> None:
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, template="plotly_dark") -> None:
        self.template = template

    def set_template(self, template: str) -> None:
        self.template = template

    def get_template(self) -> str:
        return self.template


class PriceChangeEntry:
    def __init__(self, change_label, change_value) -> None:
        self.strEntry = change_label
        if change_value is None:
            self.strPercentage = "N/A"
        else:
            self.strPercentage = f"{change_value:.1f}%"


class GeneralDataEntry:
    def __init__(self, data_emoji, data_type, data_value) -> None:
        self.emoji = data_emoji
        self.type = data_type
        if data_value == "N/A" or data_value is None:
            self.value = "N/A"
        else:
            self.value = human_format(float(data_value))


class AtEntry:
    def __init__(self, allt_emoji, allt_symbol, allt_price, allt_percentage, allt_date) -> None:
        self.emoji = allt_emoji
        self.symbol = allt_symbol
        if allt_price and "usd" in allt_price:
            self.at_price = human_format(allt_price["usd"]) + "$"
        else:
            self.at_price = "N/A"
        if allt_percentage and "usd" in allt_percentage:
            self.at_percentage = human_format(allt_percentage["usd"]) + "%"
        else:
            self.at_percentage = "N/A"
        if allt_date and "usd" in allt_date:
            self.date = format_date(allt_date["usd"])
        else:
            self.date = "N/A"
