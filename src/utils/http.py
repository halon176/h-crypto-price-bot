import logging

import httpx

from src.config import settings as s

api_headers = {"X-API-KEY": s.hcpb_api_key.get_secret_value()} if s.hcpb_api_key else None


async def fetch_url(url: str, headers: dict[str, str] | None = None) -> dict | list | None:
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


async def write_call(service_id: int, type_id: int, chat_id: str, coin: str | None = None) -> bool:
    if not s.hcpb_api_url:
        return True
    url = f"{s.hcpb_api_url}/calls"
    data = {"service_id": service_id, "type_id": type_id, "chat_id": chat_id, "coin": coin}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=api_headers)
            if response.status_code != 401:
                return True
            else:
                return False
    except Exception as e:
        logging.error(f"Error tracking API: {str(e)}")
        return True


async def get_excluded() -> list[str]:
    url = f"{s.hcpb_api_url}/excluded"
    try:
        excluded = await fetch_url(url, headers=api_headers)
        if not excluded:
            return []
        return excluded
    except Exception as e:
        logging.error(f"Error fetching excluded: {str(e)}")
        return []
