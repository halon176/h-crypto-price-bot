"""Formatting utilities for the crypto price bot."""

from datetime import datetime
from typing import Protocol, TypeVar

from telegramify_markdown import markdownify

from src.constants import COLUMN_SEPARATOR


class FormattableEntry(Protocol):
    """Protocol for entries that can be formatted into columns."""

    def get_columns(self) -> tuple[str, ...]:
        """Return tuple of column values for this entry."""
        ...


T = TypeVar("T", bound=FormattableEntry)


def format_date(date_str: str) -> str:
    """Format ISO date string to MM/YY format.

    Args:
        date_str: ISO format date string (e.g., "2024-01-15T00:00:00Z")

    Returns:
        Formatted date string in MM/YY format
    """
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime("%m/%y")


def max_column_size(values: list[str]) -> int:
    """Calculate maximum string length in a list.

    Args:
        values: List of strings to measure

    Returns:
        Length of longest string, or 0 if list is empty
    """
    try:
        return max(len(value) for value in values)
    except ValueError:
        return 0


def human_format(num: float) -> str:
    """Format large numbers with K/M/B/T suffixes.

    Args:
        num: Number to format

    Returns:
        Formatted string (e.g., 1500 -> "1.5K", 1000000 -> "1M")
    """
    magnitude = 0
    suffixes = ["", "K", "M", "B", "T"]
    max_suffix_index = len(suffixes) - 1

    while abs(num) >= 1000 and magnitude < max_suffix_index:
        magnitude += 1
        num /= 1000.0

    num = float(f"{num:.3g}")
    additional_digits = max(int(magnitude - max_suffix_index), 0)

    formatted_num = f"{num:f}".rstrip("0").rstrip(".")
    formatted_num += "0" * additional_digits

    return f"{formatted_num}{suffixes[magnitude]}"


def mk2_formatter(text: str) -> str:
    """Format text for Telegram MarkdownV2.

    Args:
        text: Text to format

    Returns:
        Formatted text compatible with Telegram MarkdownV2
    """
    return markdownify(
        text,
        max_line_length=None,
        normalize_whitespace=False,
        latex_escape=False
    )


def format_table(
    entries: list[tuple[str, ...]],
    alignments: list[str] | None = None
) -> str:
    """Format a list of entries into a aligned table.

    Args:
        entries: List of tuples, each representing a row
        alignments: Optional list of alignment specifiers ('left', 'right')
                   for each column. Defaults to all left-aligned.

    Returns:
        Formatted table string with aligned columns

    Example:
        >>> entries = [("BTC", "50000", "+5.2%"), ("ETH", "3000", "-1.5%")]
        >>> format_table(entries, ["left", "right", "right"])
        "BTC    50000    +5.2%\\nETH     3000    -1.5%"
    """
    if not entries:
        return ""

    num_columns = len(entries[0])
    if alignments is None:
        alignments = ["left"] * num_columns

    # Calculate column widths
    column_widths = []
    for col_idx in range(num_columns):
        max_width = max(len(row[col_idx]) for row in entries)
        column_widths.append(max_width)

    # Format rows
    formatted_rows = []
    for row in entries:
        formatted_cols = []
        for col_idx, value in enumerate(row):
            width = column_widths[col_idx]
            alignment = alignments[col_idx]

            if alignment == "right":
                formatted_value = value.rjust(width)
            else:
                formatted_value = value.ljust(width)

            formatted_cols.append(formatted_value)

        formatted_rows.append(COLUMN_SEPARATOR.join(formatted_cols))

    return "\n".join(formatted_rows)


def format_price(price: float, decimals: int = 2) -> str:
    """Format price value with appropriate decimal places.

    Args:
        price: Price value to format
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1, include_sign: bool = True) -> str:
    """Format percentage value.

    Args:
        value: Percentage value to format
        decimals: Number of decimal places (default: 1)
        include_sign: Whether to include + sign for positive values

    Returns:
        Formatted percentage string with % symbol
    """
    sign = "+" if include_sign and value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"
