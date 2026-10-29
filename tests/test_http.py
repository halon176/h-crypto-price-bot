import asyncio

import httpx
import pytest

from src.utils import http


@pytest.fixture
def api_status(monkeypatch):
    """Answer every hcpb-api request with the given status code."""

    def install(status):
        transport = httpx.MockTransport(lambda request: httpx.Response(status))
        real_client = httpx.AsyncClient
        monkeypatch.setattr(http.httpx, "AsyncClient", lambda **kwargs: real_client(transport=transport, **kwargs))

    monkeypatch.setattr(http.s, "hcpb_api_url", "http://hcpb-api")
    return install


@pytest.mark.parametrize(("status", "allowed"), [(201, True), (429, False), (401, True), (500, True)])
def test_write_call_blocks_only_on_429(api_status, status, allowed):
    api_status(status)

    assert asyncio.run(http.write_call(1, 1, "42", "bitcoin")) is allowed
