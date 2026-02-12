"""Tests for formatting utilities."""

import pytest

from src.utils.formatters import (
    format_date,
    max_column_size,
    human_format,
    format_table,
    format_price,
    format_percentage,
)


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_basic(self):
        """Test basic date formatting."""
        result = format_date("2024-01-15T00:00:00Z")
        assert result == "01/24"

    def test_format_date_different_month(self):
        """Test date formatting with different month."""
        result = format_date("2021-11-10T14:24:11Z")
        assert result == "11/21"

    def test_format_date_december(self):
        """Test date formatting for December."""
        result = format_date("2023-12-31T23:59:59Z")
        assert result == "12/23"

    def test_format_date_january(self):
        """Test date formatting for January."""
        result = format_date("2025-01-01T00:00:00Z")
        assert result == "01/25"


class TestMaxColumnSize:
    """Tests for max_column_size function."""

    def test_max_column_size_simple(self):
        """Test finding max column size."""
        values = ["BTC", "ETH", "USDT"]
        assert max_column_size(values) == 4  # "USDT" is longest

    def test_max_column_size_varied_lengths(self):
        """Test with varied length strings."""
        values = ["a", "abc", "ab", "abcdef"]
        assert max_column_size(values) == 6

    def test_max_column_size_empty_list(self):
        """Test with empty list."""
        assert max_column_size([]) == 0

    def test_max_column_size_single_item(self):
        """Test with single item."""
        assert max_column_size(["Bitcoin"]) == 7

    def test_max_column_size_all_same_length(self):
        """Test when all strings have same length."""
        values = ["aaa", "bbb", "ccc"]
        assert max_column_size(values) == 3


class TestHumanFormat:
    """Tests for human_format function."""

    def test_human_format_less_than_thousand(self):
        """Test numbers less than 1000."""
        assert human_format(500) == "500"
        assert human_format(999) == "999"

    def test_human_format_thousands(self):
        """Test thousands formatting."""
        assert human_format(1000) == "1K"
        assert human_format(1500) == "1.5K"
        assert human_format(999000) == "999K"

    def test_human_format_millions(self):
        """Test millions formatting."""
        assert human_format(1000000) == "1M"
        assert human_format(2500000) == "2.5M"
        assert human_format(999000000) == "999M"

    def test_human_format_billions(self):
        """Test billions formatting."""
        assert human_format(1000000000) == "1B"
        assert human_format(1500000000) == "1.5B"
        assert human_format(42000000000) == "42B"

    def test_human_format_trillions(self):
        """Test trillions formatting."""
        assert human_format(1000000000000) == "1T"
        assert human_format(3500000000000) == "3.5T"

    def test_human_format_negative_numbers(self):
        """Test negative numbers."""
        assert human_format(-1000) == "-1K"
        assert human_format(-1500000) == "-1.5M"

    def test_human_format_zero(self):
        """Test zero."""
        assert human_format(0) == "0"

    def test_human_format_small_decimals(self):
        """Test small decimal numbers."""
        assert human_format(0.5) == "0.5"
        assert human_format(123.45) == "123"


class TestFormatTable:
    """Tests for format_table function."""

    def test_format_table_simple(self):
        """Test simple table formatting."""
        entries = [
            ("BTC", "50000", "+5.2%"),
            ("ETH", "3000", "-1.5%")
        ]
        result = format_table(entries, ["left", "right", "right"])
        lines = result.split("\n")
        assert len(lines) == 2
        assert "BTC" in lines[0]
        assert "ETH" in lines[1]

    def test_format_table_default_alignment(self):
        """Test table with default left alignment."""
        entries = [("A", "B"), ("C", "D")]
        result = format_table(entries)
        assert "A" in result
        assert "B" in result

    def test_format_table_empty_list(self):
        """Test formatting empty list."""
        result = format_table([])
        assert result == ""

    def test_format_table_single_column(self):
        """Test table with single column."""
        entries = [("BTC",), ("ETH",), ("ADA",)]
        result = format_table(entries)
        lines = result.split("\n")
        assert len(lines) == 3

    def test_format_table_alignment(self):
        """Test that alignment works correctly."""
        entries = [
            ("Short", "LongValue"),
            ("VeryLongText", "Val")
        ]
        result = format_table(entries, ["left", "right"])
        lines = result.split("\n")
        # First line should have spaces after "Short"
        # Second line should have spaces before "Val"
        assert len(lines[0]) == len(lines[1])

    def test_format_table_varied_widths(self):
        """Test table with varied column widths."""
        entries = [
            ("A", "B", "C"),
            ("AA", "BB", "CC"),
            ("AAA", "BBB", "CCC")
        ]
        result = format_table(entries)
        lines = result.split("\n")
        # All lines should have the same length
        assert len(set(len(line) for line in lines)) == 1


class TestFormatPrice:
    """Tests for format_price function."""

    def test_format_price_default_decimals(self):
        """Test price formatting with default 2 decimals."""
        assert format_price(123.456) == "123.46"
        assert format_price(50000.0) == "50000.00"

    def test_format_price_custom_decimals(self):
        """Test price formatting with custom decimals."""
        assert format_price(123.456, decimals=0) == "123"
        assert format_price(123.456, decimals=1) == "123.5"
        assert format_price(123.456, decimals=3) == "123.456"

    def test_format_price_zero(self):
        """Test formatting zero price."""
        assert format_price(0) == "0.00"
        assert format_price(0, decimals=0) == "0"

    def test_format_price_small_number(self):
        """Test formatting small numbers."""
        assert format_price(0.12345) == "0.12"
        assert format_price(0.12345, decimals=4) == "0.1235"

    def test_format_price_large_number(self):
        """Test formatting large numbers."""
        assert format_price(1234567.89) == "1234567.89"


class TestFormatPercentage:
    """Tests for format_percentage function."""

    def test_format_percentage_positive_with_sign(self):
        """Test positive percentage with sign."""
        assert format_percentage(5.2) == "+5.2%"
        assert format_percentage(10.0) == "+10.0%"

    def test_format_percentage_negative(self):
        """Test negative percentage."""
        assert format_percentage(-3.1) == "-3.1%"
        assert format_percentage(-0.5) == "-0.5%"

    def test_format_percentage_zero(self):
        """Test zero percentage."""
        result = format_percentage(0.0)
        assert result == "0.0%" or result == "+0.0%"

    def test_format_percentage_without_sign(self):
        """Test percentage without plus sign."""
        assert format_percentage(5.2, include_sign=False) == "5.2%"
        assert format_percentage(-3.1, include_sign=False) == "-3.1%"

    def test_format_percentage_custom_decimals(self):
        """Test percentage with custom decimals."""
        assert format_percentage(5.6789, decimals=0) == "+6%"
        assert format_percentage(5.6789, decimals=2) == "+5.68%"
        assert format_percentage(5.6789, decimals=3) == "+5.679%"

    def test_format_percentage_large_value(self):
        """Test very large percentage."""
        assert format_percentage(999.9) == "+999.9%"
        assert format_percentage(1000.0) == "+1000.0%"

    def test_format_percentage_small_value(self):
        """Test very small percentage."""
        assert format_percentage(0.01, decimals=2) == "+0.01%"
        assert format_percentage(-0.01, decimals=2) == "-0.01%"

    def test_format_percentage_rounding(self):
        """Test that rounding works correctly."""
        assert format_percentage(5.66, decimals=1) == "+5.7%"
        assert format_percentage(5.64, decimals=1) == "+5.6%"
