"""Tests for data models."""

import pytest

from src.models import (
    PriceChangeEntry,
    GeneralDataEntry,
    AtEntry,
    MarketCapEntry,
    CoinInfo,
    CallbackData,
)


class TestPriceChangeEntry:
    """Tests for PriceChangeEntry model."""

    def test_price_change_with_value(self):
        """Test price change entry with valid value."""
        entry = PriceChangeEntry("24h", 5.2)
        assert entry.entry == "24h"
        assert entry.percentage == "5.2%"

    def test_price_change_with_negative_value(self):
        """Test price change entry with negative value."""
        entry = PriceChangeEntry("7d", -3.1)
        assert entry.entry == "7d"
        assert entry.percentage == "-3.1%"

    def test_price_change_with_none_value(self):
        """Test price change entry with None value."""
        entry = PriceChangeEntry("30d", None)
        assert entry.entry == "30d"
        assert entry.percentage == "N/A"

    def test_price_change_with_zero_value(self):
        """Test price change entry with zero value."""
        entry = PriceChangeEntry("1y", 0.0)
        assert entry.entry == "1y"
        assert entry.percentage == "0.0%"

    def test_price_change_formatting_precision(self):
        """Test that percentage is formatted to 1 decimal place."""
        entry = PriceChangeEntry("24h", 5.6789)
        assert entry.percentage == "5.7%"


class TestGeneralDataEntry:
    """Tests for GeneralDataEntry model."""

    def test_general_data_with_number(self):
        """Test general data entry with numeric value."""
        entry = GeneralDataEntry("💰", "M. Cap", 1500000000)
        assert entry.emoji == "💰"
        assert entry.entry == "M. Cap"
        assert entry.value == "1.5B"  # Should be human formatted

    def test_general_data_with_string_number(self):
        """Test general data entry with string numeric value."""
        entry = GeneralDataEntry("💵", "Circ. S", "2500000")
        assert entry.value == "2.5M"

    def test_general_data_with_na_string(self):
        """Test general data entry with 'N/A' string."""
        entry = GeneralDataEntry("🖨", "Total S", "N/A")
        assert entry.value == "N/A"

    def test_general_data_with_none(self):
        """Test general data entry with None value."""
        entry = GeneralDataEntry("💎", "Max S", None)
        assert entry.value == "N/A"

    def test_general_data_small_number(self):
        """Test general data entry with small number."""
        entry = GeneralDataEntry("💰", "Price", 500)
        assert entry.value == "500"


class TestAtEntry:
    """Tests for AtEntry (All-Time High/Low) model."""

    def test_ath_entry_with_full_data(self):
        """Test ATH entry with complete data."""
        entry = AtEntry(
            emoji="📈",
            symbol="ATH",
            price={"usd": 69000},
            percentage={"usd": -25.5},
            date={"usd": "2021-11-10T14:24:11.849Z"}
        )
        assert entry.emoji == "📈"
        assert entry.symbol == "ATH"
        assert entry.price == "69K$"
        assert entry.percentage == "-25.5%"
        assert entry.date == "11/21"

    def test_atl_entry_with_full_data(self):
        """Test ATL entry with complete data."""
        entry = AtEntry(
            emoji="📉",
            symbol="ATL",
            price={"usd": 0.05},
            percentage={"usd": 999999.9},
            date={"usd": "2013-07-05T00:00:00.000Z"}
        )
        assert entry.emoji == "📉"
        assert entry.symbol == "ATL"
        assert entry.price == "0.05$"
        assert "%" in entry.percentage
        assert entry.date == "07/13"

    def test_at_entry_with_missing_price(self):
        """Test AT entry with missing price data."""
        entry = AtEntry(
            emoji="📈",
            symbol="ATH",
            price=None,
            percentage={"usd": -10.0},
            date={"usd": "2021-11-10T14:24:11.849Z"}
        )
        assert entry.price == "N/A"

    def test_at_entry_with_missing_percentage(self):
        """Test AT entry with missing percentage data."""
        entry = AtEntry(
            emoji="📈",
            symbol="ATH",
            price={"usd": 50000},
            percentage=None,
            date={"usd": "2021-11-10T14:24:11.849Z"}
        )
        assert entry.percentage == "N/A"

    def test_at_entry_with_missing_date(self):
        """Test AT entry with missing date data."""
        entry = AtEntry(
            emoji="📈",
            symbol="ATH",
            price={"usd": 50000},
            percentage={"usd": -10.0},
            date=None
        )
        assert entry.date == "N/A"

    def test_at_entry_all_none(self):
        """Test AT entry with all None values."""
        entry = AtEntry("📈", "ATH", None, None, None)
        assert entry.price == "N/A"
        assert entry.percentage == "N/A"
        assert entry.date == "N/A"


class TestMarketCapEntry:
    """Tests for MarketCapEntry model."""

    def test_market_cap_from_tuple(self):
        """Test creating MarketCapEntry from tuple."""
        entry = MarketCapEntry.from_tuple(("btc", 45.5))
        assert entry.symbol == "BTC"
        assert entry.percentage == "45.5%"

    def test_market_cap_from_tuple_lowercase(self):
        """Test symbol is uppercased."""
        entry = MarketCapEntry.from_tuple(("eth", 18.2))
        assert entry.symbol == "ETH"

    def test_market_cap_formatting(self):
        """Test percentage formatting precision."""
        entry = MarketCapEntry.from_tuple(("usdt", 4.6789))
        assert entry.percentage == "4.7%"

    def test_market_cap_zero_percentage(self):
        """Test with zero percentage."""
        entry = MarketCapEntry.from_tuple(("sol", 0.0))
        assert entry.percentage == "0.0%"


class TestCoinInfo:
    """Tests for CoinInfo model."""

    def test_coin_info_creation(self):
        """Test creating CoinInfo."""
        coin = CoinInfo(id="bitcoin", symbol="btc", name="Bitcoin")
        assert coin.id == "bitcoin"
        assert coin.symbol == "btc"
        assert coin.name == "Bitcoin"

    def test_coin_info_to_dict(self):
        """Test converting CoinInfo to dictionary."""
        coin = CoinInfo(id="ethereum", symbol="eth", name="Ethereum")
        data = coin.to_dict()
        assert data == {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum"
        }

    def test_coin_info_from_dict(self):
        """Test creating CoinInfo from dictionary."""
        data = {"id": "cardano", "symbol": "ada", "name": "Cardano"}
        coin = CoinInfo.from_dict(data)
        assert coin.id == "cardano"
        assert coin.symbol == "ada"
        assert coin.name == "Cardano"

    def test_coin_info_round_trip(self):
        """Test converting to dict and back."""
        original = CoinInfo(id="polkadot", symbol="dot", name="Polkadot")
        data = original.to_dict()
        restored = CoinInfo.from_dict(data)
        assert restored.id == original.id
        assert restored.symbol == original.symbol
        assert restored.name == original.name


class TestCallbackData:
    """Tests for CallbackData model."""

    def test_parse_simple_callback(self):
        """Test parsing simple callback without action."""
        data = CallbackData.parse("chart.bitcoin")
        assert data.prefix == "chart"
        assert data.action == ""
        assert data.value == "bitcoin"

    def test_parse_callback_with_action(self):
        """Test parsing callback with action."""
        data = CallbackData.parse("theme_dark.bitcoin")
        assert data.prefix == "theme"
        assert data.action == "dark"
        assert data.value == "bitcoin"

    def test_parse_period_callback(self):
        """Test parsing period callback."""
        data = CallbackData.parse("period_30.ethereum")
        assert data.prefix == "period"
        assert data.action == "30"
        assert data.value == "ethereum"

    def test_parse_invalid_callback_no_dot(self):
        """Test parsing invalid callback without dot."""
        with pytest.raises(ValueError, match="Invalid callback format"):
            CallbackData.parse("invalid_callback")

    def test_parse_cmc_callback(self):
        """Test parsing CMC callback."""
        data = CallbackData.parse("cmc.1234")
        assert data.prefix == "cmc"
        assert data.action == ""
        assert data.value == "1234"

    def test_format_simple_callback(self):
        """Test formatting callback without action."""
        data = CallbackData(prefix="chart", action="", value="bitcoin")
        assert data.format() == "chart.bitcoin"

    def test_format_callback_with_action(self):
        """Test formatting callback with action."""
        data = CallbackData(prefix="theme", action="dark", value="bitcoin")
        assert data.format() == "theme_dark.bitcoin"

    def test_format_period_callback(self):
        """Test formatting period callback."""
        data = CallbackData(prefix="period", action="90", value="solana")
        assert data.format() == "period_90.solana"

    def test_callback_round_trip(self):
        """Test parsing and formatting round trip."""
        original = "period_7.cardano"
        parsed = CallbackData.parse(original)
        formatted = parsed.format()
        assert formatted == original

    def test_callback_round_trip_simple(self):
        """Test parsing and formatting round trip for simple callback."""
        original = "chart.ethereum"
        parsed = CallbackData.parse(original)
        formatted = parsed.format()
        assert formatted == original

    def test_parse_multiple_underscores(self):
        """Test parsing with multiple underscores in action."""
        data = CallbackData.parse("prefix_action_value.coinid")
        assert data.prefix == "prefix"
        assert data.action == "action_value"
        assert data.value == "coinid"

    def test_parse_multiple_dots(self):
        """Test parsing with multiple dots."""
        data = CallbackData.parse("prefix.value.with.dots")
        assert data.prefix == "prefix"
        assert data.action == ""
        assert data.value == "value.with.dots"
