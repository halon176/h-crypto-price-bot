from datetime import datetime

from telegramify_markdown import markdownify


def format_date(date_str: str) -> str:
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime("%m/%y")


def max_column_size(arr: list[str]) -> int:
    try:
        return max(len(string) for string in arr)
    except ValueError:
        return 0


def human_format(num: float) -> str:
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
    return markdownify(text, max_line_length=None, normalize_whitespace=False)
