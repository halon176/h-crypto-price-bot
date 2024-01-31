import logging
from datetime import datetime

import httpx


def format_date(date_str: str) -> str:
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime("%m/%y")


def max_column_size(arr: list) -> int:
    return max(len(string) for string in arr)


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


async def fetch_url(url: str, headers: dict[str, str] | None = None) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            # Utilizza l'argomento headers se è stato fornito, altrimenti usa un dizionario vuoto
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to fetch URL {url}, status code: {response.status_code}")
                return None
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {str(e)}")
        return None


def mk2_formatter(text: str) -> str:
    """
    function to place escape character before specific symbols, if there is not one
    :param text:
    :return:
    """
    symbols: list = ["_", "*", "~", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for symbol in symbols:
        index = text.find(symbol)
        while index != -1:
            if index > 0 and text[index - 1] != "\\":
                text = text[:index] + "\\" + text[index:]
            index = text.find(symbol, index + 2)
    return text
