import datetime
import logging

import httpx

from .config import settings as s


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
