import logging
from datetime import datetime
from typing import Optional, Dict

import httpx


def format_date(date_str):
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime("%m/%y")


def max_column_size(arr):
    return max((len(string) for string in arr))


def human_format(num) -> str:
    magnitude = 0
    suffixes = ["", "K", "M", "B", "T"]
    max_suffix_index = len(suffixes) - 1

    while abs(num) >= 1000 and magnitude < max_suffix_index:
        magnitude += 1
        num /= 1000.0

    num = float("{:.3g}".format(num))
    additional_digits = max(int(magnitude - max_suffix_index), 0)

    formatted_num = "{:f}".format(num).rstrip("0").rstrip(".")

    formatted_num += "0" * additional_digits

    return "{}{}".format(formatted_num, suffixes[magnitude])


async def fetch_url(
    url: str, headers: Optional[Dict[str, str]] = None
) -> Optional[dict]:
    try:
        async with httpx.AsyncClient() as client:
            # Utilizza l'argomento headers se è stato fornito, altrimenti usa un dizionario vuoto
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(
                    f"Failed to fetch URL {url}, status code: {response.status_code}"
                )
                return None
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {str(e)}")
        return None
