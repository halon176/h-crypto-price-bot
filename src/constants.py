"""Constants and configuration values for the crypto price bot."""

from enum import StrEnum
from typing import Final

# API Endpoints
COINGECKO_API_BASE: Final[str] = "https://api.coingecko.com/api/v3"
COINGECKO_API_COINS: Final[str] = f"{COINGECKO_API_BASE}/coins/"
COINGECKO_API_GLOBAL: Final[str] = f"{COINGECKO_API_BASE}/global"
COINGECKO_API_COINS_LIST: Final[str] = f"{COINGECKO_API_BASE}/coins/list"
COINGECKO_CHART_BASE: Final[str] = "https://www.coingecko.com/coins/"

COINMARKETCAP_API_BASE: Final[str] = "https://pro-api.coinmarketcap.com/v1"
COINMARKETCAP_API_MAP: Final[str] = f"{COINMARKETCAP_API_BASE}/cryptocurrency/map"
COINMARKETCAP_API_QUOTES: Final[str] = f"{COINMARKETCAP_API_BASE}/cryptocurrency/quotes/latest"

ETHERSCAN_API_BASE: Final[str] = "https://api.etherscan.io/api"

HCPB_API_BASE: Final[str] = "https://hcpb-api.onrender.com"
HCPB_API_TRACK: Final[str] = f"{HCPB_API_BASE}/track"

COINDESK_RSS_URL: Final[str] = "https://www.coindesk.com/arc/outboundfeeds/rss/"

# Cache TTL
COIN_LIST_CACHE_HOURS: Final[int] = 1
COIN_LIST_CACHE_SECONDS: Final[int] = COIN_LIST_CACHE_HOURS * 3600

# Rate Limiting
MAX_REQUESTS_PER_HOUR: Final[int] = 10

# Ethereum Gas
GAS_LIMIT_STANDARD_TRANSFER: Final[int] = 21000
GWEI_TO_ETH: Final[int] = 1_000_000_000

# Chart Configuration
class ChartPeriod(StrEnum):
    """Available chart time periods."""
    ONE_DAY = "1"
    SEVEN_DAYS = "7"
    THIRTY_DAYS = "30"
    NINETY_DAYS = "90"
    ONE_YEAR = "365"


class ChartTheme(StrEnum):
    """Available chart themes."""
    LIGHT = "light"
    DARK = "dark"


CHART_PERIOD_LABELS: Final[dict[ChartPeriod, str]] = {
    ChartPeriod.ONE_DAY: "1d",
    ChartPeriod.SEVEN_DAYS: "7d",
    ChartPeriod.THIRTY_DAYS: "30d",
    ChartPeriod.NINETY_DAYS: "90d",
    ChartPeriod.ONE_YEAR: "1y",
}

# Callback Data Prefixes
class CallbackPrefix(StrEnum):
    """Prefixes for callback query data."""
    CG = "cg"
    CMC = "cmc"
    CHART = "chart"
    THEME = "theme"
    PERIOD = "period"


# Emojis
POSITIONAL_EMOJIS: Final[list[str]] = [
    "🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
]

MOOD_EMOJIS: Final[list[str]] = ["😎", "😄", "🤨", "😰", "💀"]

# Message Templates
MESSAGE_RATE_LIMIT_EXCEEDED: Final[str] = (
    "You have reached the maximum number of requests allowed per hour. "
    "Please try again later."
)

MESSAGE_COIN_NOT_FOUND: Final[str] = (
    "The cryptocurrency '{}' was not found. "
    "Please check the symbol and try again."
)

MESSAGE_INVALID_THEME: Final[str] = (
    "Invalid theme selected. Please choose either 'light' or 'dark'."
)

MESSAGE_NO_ARGS_PROVIDED: Final[str] = (
    "Please provide a cryptocurrency symbol. "
    "Example: /price btc"
)

# Formatting
COLUMN_SEPARATOR: Final[str] = "    "
PRICE_DECIMAL_PLACES: Final[int] = 2
PERCENTAGE_DECIMAL_PLACES: Final[int] = 1

# CoinGecko Exclusions
COINGECKO_EXCLUDED_IDS: Final[list[str]] = [
    "matic-network",
    "binancecoin",
    "crypto-com-chain",
]

# Display Limits
MAX_MARKET_CAP_ENTRIES: Final[int] = 10
MAX_NEWS_ITEMS: Final[int] = 5
