import os
from typing import Any

import aiohttp

from app.core.security import create_hmac_signature


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _request(
        self, method: str, path: str, json: dict | None = None
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {}
        body = b""
        if json:
            import json as json_lib
            body = json_lib.dumps(json, sort_keys=True).encode("utf-8")
            headers["Content-Type"] = "application/json"
            headers["X-Signature"] = create_hmac_signature(body)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, json=json, headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def post(self, path: str, json: dict) -> Any:
        return await self._request("POST", path, json=json)

    async def get(self, path: str) -> Any:
        return await self._request("GET", path)


api_client = ApiClient(base_url=os.getenv("API_BASE_URL", "http://api:8000/api/v1"))
