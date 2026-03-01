"""Data models for the crypto price bot."""

from dataclasses import dataclass
from typing import Any


@dataclass
class PriceChangeEntry:
    """Represents a price change entry with label and formatted percentage."""

    label: str
    """Time period label (e.g., '24h', '7d')."""
    formatted_percentage: str
    """Formatted percentage string (e.g., '1.5%' or 'N/A')."""

    @classmethod
    def from_raw(cls, label: str, value: float | None) -> "PriceChangeEntry":
        """Create a PriceChangeEntry from a raw percentage value.

        Args:
            label: Time period label (e.g., '24h', '7d')
            value: Raw percentage change value, or None if not available

        Returns:
            PriceChangeEntry with formatted percentage
        """
        return cls(
            label=label,
            formatted_percentage="N/A" if value is None else f"{value:.1f}%",
        )


@dataclass
class GeneralDataEntry:
    """Represents a general data entry with emoji, label and formatted value."""

    emoji: str
    """Display emoji (e.g., '💰')."""
    label: str
    """Display label (e.g., 'M. Cap', 'Circ. S')."""
    formatted_value: str
    """Human-formatted value (e.g., '1.2B') or 'N/A'."""

    @classmethod
    def from_raw(cls, emoji: str, label: str, value: Any) -> "GeneralDataEntry":
        """Create a GeneralDataEntry from a raw numeric value.

        Args:
            emoji: Display emoji
            label: Display label
            value: Raw numeric value, 'N/A', or None

        Returns:
            GeneralDataEntry with human-formatted value
        """
        from src.utils.formatters import human_format

        return cls(
            emoji=emoji,
            label=label,
            formatted_value="N/A" if (value == "N/A" or value is None) else human_format(float(value)),
        )


class AtEntry:
    """Represents an all-time high/low entry."""

    def __init__(
        self,
        emoji: str,
        symbol: str,
        price: dict[str, float] | None,
        percentage: dict[str, float] | None,
        date: dict[str, str] | None
    ) -> None:
        """Initialize all-time entry.

        Args:
            emoji: Emoji to display (e.g., 📈 for ATH, 📉 for ATL)
            symbol: Symbol/label (e.g., 'ATH', 'ATL')
            price: Price dictionary with USD value
            percentage: Percentage change dictionary with USD value
            date: Date dictionary with USD value
        """
        from src.utils.formatters import format_date, human_format

        self.emoji = emoji
        self.symbol = symbol

        if price and "usd" in price:
            self.price = human_format(price["usd"]) + "$"
        else:
            self.price = "N/A"

        if percentage and "usd" in percentage:
            self.percentage = human_format(percentage["usd"]) + "%"
        else:
            self.percentage = "N/A"

        if date and "usd" in date:
            self.date = format_date(date["usd"])
        else:
            self.date = "N/A"


@dataclass
class MarketCapEntry:
    """Represents a market capitalization entry with symbol and percentage."""

    symbol: str
    percentage: str

    @classmethod
    def from_tuple(cls, data: tuple[str, float]) -> "MarketCapEntry":
        """Create a MarketCapEntry from a tuple of (symbol, percentage).

        Args:
            data: Tuple containing (symbol, percentage_value)

        Returns:
            MarketCapEntry instance
        """
        return cls(
            symbol=data[0].upper(),
            percentage=f"{data[1]:.1f}%"
        )


@dataclass
class GasEntry:
    """Represents a gas price entry with speed and cost information."""

    speed: str
    gwei: str
    usd: str
    time: str

    @classmethod
    def from_data(
        cls,
        speed: str,
        gas_price_gwei: float,
        eth_price_usd: float,
        time: str
    ) -> "GasEntry":
        """Create a GasEntry from raw data.

        Args:
            speed: Transaction speed descriptor (e.g., "Fast", "Standard")
            gas_price_gwei: Gas price in Gwei
            eth_price_usd: Current ETH price in USD
            time: Estimated confirmation time

        Returns:
            GasEntry instance with formatted values
        """
        from src.constants import GAS_LIMIT_STANDARD_TRANSFER, GWEI_TO_ETH

        gas_cost_eth = (gas_price_gwei * GAS_LIMIT_STANDARD_TRANSFER) / GWEI_TO_ETH
        gas_cost_usd = gas_cost_eth * eth_price_usd

        return cls(
            speed=speed,
            gwei=f"{gas_price_gwei:.2f}",
            usd=f"${gas_cost_usd:.2f}",
            time=time
        )


@dataclass
class CoinInfo:
    """Information about a cryptocurrency."""

    id: str
    symbol: str
    name: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with id, symbol, and name
        """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CoinInfo":
        """Create CoinInfo from dictionary.

        Args:
            data: Dictionary containing coin information

        Returns:
            CoinInfo instance
        """
        return cls(
            id=data["id"],
            symbol=data["symbol"],
            name=data["name"]
        )


@dataclass
class CallbackData:
    """Parsed callback query data."""

    prefix: str
    action: str
    value: str

    @classmethod
    def parse(cls, callback_string: str) -> "CallbackData":
        """Parse callback query data string.

        Expected format: "prefix.value" or "prefix_action.value"
        Examples:
            - "chart.bitcoin" -> CallbackData("chart", "", "bitcoin")
            - "theme_dark.bitcoin" -> CallbackData("theme", "dark", "bitcoin")

        Args:
            callback_string: The callback data string to parse

        Returns:
            CallbackData instance

        Raises:
            ValueError: If callback_string format is invalid
        """
        if "." not in callback_string:
            raise ValueError(f"Invalid callback format: {callback_string}")

        prefix_part, value = callback_string.split(".", 1)

        if "_" in prefix_part:
            prefix, action = prefix_part.split("_", 1)
        else:
            prefix = prefix_part
            action = ""

        return cls(prefix=prefix, action=action, value=value)

    def format(self) -> str:
        """Format callback data back to string.

        Returns:
            Formatted callback string
        """
        if self.action:
            return f"{self.prefix}_{self.action}.{self.value}"
        return f"{self.prefix}.{self.value}"
