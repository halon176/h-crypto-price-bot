"""Shared singleton classes and global instances."""

import datetime
import logging

from src.config import settings as s
from src.utils.http import fetch_url, get_excluded


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

    async def update(self) -> None:
        cmc_api_key = s.CMC_API_KEY.get_secret_value()
        if not cmc_api_key:
            return
        now = datetime.datetime.now()
        if (now - self.coin_last_update) >= datetime.timedelta(hours=1):
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
            coin_list_cmc = await fetch_url(url, headers={"X-CMC_PRO_API_KEY": cmc_api_key})
            if not coin_list_cmc:
                logging.error("Failed to fetch CoinMarketCap, list not updated")
                return
            self.coin_list = coin_list_cmc
            self.coin_last_update = now
            logging.info("Reloaded coin list from CoinMarketCap API")


class CGCoinList(CoinList):
    async def update(self) -> None:
        now = datetime.datetime.now()
        if (now - self.coin_last_update) >= datetime.timedelta(hours=1):
            url = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
            coin_request = await fetch_url(url)
            if not coin_request:
                logging.error("Failed to fetch CoinGecko, list not updated")
                return
            self.coin_list = coin_request
            self.coin_last_update = now
            excluded_values = await get_excluded()
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


# Global singleton instances
cg_coin_list = CGCoinList()
cmc_coin_list = CMCCoinList()
chart_template = ChartTemplate()
