"""Tests for constants module."""


from src.constants import (
    CHART_PERIOD_LABELS,
    COINGECKO_API_BASE,
    COINGECKO_API_COINS,
    COINMARKETCAP_API_BASE,
    GAS_LIMIT_STANDARD_TRANSFER,
    GWEI_TO_ETH,
    MESSAGE_RATE_LIMIT_EXCEEDED,
    POSITIONAL_EMOJIS,
    CallbackPrefix,
    ChartPeriod,
    ChartTheme,
)


class TestChartPeriod:
    """Tests for ChartPeriod enum."""

    def test_chart_period_values(self):
        """Test that chart periods have correct values."""
        assert ChartPeriod.ONE_DAY == "1"
        assert ChartPeriod.SEVEN_DAYS == "7"
        assert ChartPeriod.THIRTY_DAYS == "30"
        assert ChartPeriod.NINETY_DAYS == "90"
        assert ChartPeriod.ONE_YEAR == "365"

    def test_chart_period_string_comparison(self):
        """Test that ChartPeriod can be compared with strings."""
        assert ChartPeriod.ONE_DAY == "1"
        assert ChartPeriod.THIRTY_DAYS == "30"

    def test_chart_period_iteration(self):
        """Test iterating over chart periods."""
        periods = list(ChartPeriod)
        assert len(periods) == 5
        assert ChartPeriod.ONE_DAY in periods
        assert ChartPeriod.ONE_YEAR in periods


class TestChartTheme:
    """Tests for ChartTheme enum."""

    def test_chart_theme_values(self):
        """Test that chart themes have correct values."""
        assert ChartTheme.LIGHT == "light"
        assert ChartTheme.DARK == "dark"

    def test_chart_theme_string_comparison(self):
        """Test that ChartTheme can be compared with strings."""
        assert ChartTheme.LIGHT == "light"
        assert ChartTheme.DARK == "dark"


class TestCallbackPrefix:
    """Tests for CallbackPrefix enum."""

    def test_callback_prefix_values(self):
        """Test that callback prefixes have correct values."""
        assert CallbackPrefix.CHART == "chart"
        assert CallbackPrefix.THEME == "theme"
        assert CallbackPrefix.PERIOD == "period"

    def test_callback_prefix_string_comparison(self):
        """Test that CallbackPrefix can be compared with strings."""
        assert CallbackPrefix.CHART == "chart"
        assert CallbackPrefix.THEME == "theme"

    def test_callback_prefix_value_access(self):
        """Test accessing enum values."""
        assert CallbackPrefix.CHART.value == "chart"
        assert CallbackPrefix.PERIOD.value == "period"


class TestApiEndpoints:
    """Tests for API endpoint constants."""

    def test_coingecko_endpoints(self):
        """Test CoinGecko API endpoints are properly formed."""
        assert COINGECKO_API_BASE == "https://api.coingecko.com/api/v3"
        assert COINGECKO_API_COINS.startswith(COINGECKO_API_BASE)
        assert "coins" in COINGECKO_API_COINS

    def test_coinmarketcap_endpoints(self):
        """Test CoinMarketCap API endpoints are properly formed."""
        assert COINMARKETCAP_API_BASE == "https://pro-api.coinmarketcap.com/v1"
        assert "coinmarketcap.com" in COINMARKETCAP_API_BASE


class TestEmojis:
    """Tests for emoji constants."""

    def test_positional_emojis_count(self):
        """Test that we have 10 positional emojis."""
        assert len(POSITIONAL_EMOJIS) == 10

    def test_positional_emojis_content(self):
        """Test that positional emojis start with medals."""
        assert POSITIONAL_EMOJIS[0] == "🥇"
        assert POSITIONAL_EMOJIS[1] == "🥈"
        assert POSITIONAL_EMOJIS[2] == "🥉"

    def test_positional_emojis_unique(self):
        """Test that all positional emojis are unique."""
        assert len(POSITIONAL_EMOJIS) == len(set(POSITIONAL_EMOJIS))


class TestChartPeriodLabels:
    """Tests for chart period labels mapping."""

    def test_chart_period_labels_completeness(self):
        """Test that all chart periods have labels."""
        for period in ChartPeriod:
            assert period in CHART_PERIOD_LABELS

    def test_chart_period_labels_values(self):
        """Test that labels have expected format."""
        assert CHART_PERIOD_LABELS[ChartPeriod.ONE_DAY] == "1d"
        assert CHART_PERIOD_LABELS[ChartPeriod.SEVEN_DAYS] == "7d"
        assert CHART_PERIOD_LABELS[ChartPeriod.THIRTY_DAYS] == "30d"
        assert CHART_PERIOD_LABELS[ChartPeriod.NINETY_DAYS] == "90d"
        assert CHART_PERIOD_LABELS[ChartPeriod.ONE_YEAR] == "1y"


class TestMessages:
    """Tests for message templates."""

    def test_rate_limit_message_exists(self):
        """Test that rate limit message is defined."""
        assert MESSAGE_RATE_LIMIT_EXCEEDED
        assert isinstance(MESSAGE_RATE_LIMIT_EXCEEDED, str)
        assert len(MESSAGE_RATE_LIMIT_EXCEEDED) > 0

    def test_rate_limit_message_content(self):
        """Test that rate limit message contains expected keywords."""
        msg = MESSAGE_RATE_LIMIT_EXCEEDED.lower()
        assert "request" in msg or "limit" in msg


class TestGasConstants:
    """Tests for Ethereum gas constants."""

    def test_gas_limit_standard_transfer(self):
        """Test standard transfer gas limit."""
        assert GAS_LIMIT_STANDARD_TRANSFER == 21000
        assert isinstance(GAS_LIMIT_STANDARD_TRANSFER, int)

    def test_gwei_to_eth_conversion(self):
        """Test Gwei to ETH conversion factor."""
        assert GWEI_TO_ETH == 1_000_000_000
        assert isinstance(GWEI_TO_ETH, int)

    def test_gas_calculation_example(self):
        """Test example gas cost calculation."""
        gas_price_gwei = 50
        gas_cost_eth = (gas_price_gwei * GAS_LIMIT_STANDARD_TRANSFER) / GWEI_TO_ETH
        assert gas_cost_eth == 0.00105  # 50 * 21000 / 1e9
