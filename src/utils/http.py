import logging

import httpx

from src.config import settings as s


async def fetch_url(url: str, headers: dict[str, str] | None = None) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to fetch URL {url}, status code: {response.status_code}")
                return None
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {str(e)}")
        return None


async def api_call(service_id: int, type_id: int, chat_id: str, coin: str | None = None) -> bool:
    if not s.API_URL:
        return True
    url = f"{s.API_URL}/call"
    data = {"service_id": service_id, "type_id": type_id, "chat_id": chat_id, "coin": coin}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            if response.status_code != 401:
                return True
            else:
                return False
    except Exception as e:
        logging.error(f"Error tracking API: {str(e)}")
        return True
