"""Small local HTTP client for the Vega-S ESP8266 thermostat."""
from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout


class VegaApiError(Exception):
    """The thermostat did not respond correctly."""


class VegaLocalApi:
    """Commands go to the on-board thermostat, not the relay directly."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self._base_url = f"http://{host}"
        self._timeout = ClientTimeout(total=4, connect=2)

    async def _request(self, method: str, path: str, data: dict | None = None) -> dict[str, Any]:
        try:
            async with self._session.request(
                method,
                self._base_url + path,
                data=data,
                timeout=self._timeout,
                headers={"Cache-Control": "no-store"},
                allow_redirects=False,
            ) as response:
                if response.status != 200:
                    message = (await response.text())[:120]
                    raise VegaApiError(f"HTTP {response.status}: {message}")
                payload = await response.json(content_type=None)
                if not isinstance(payload, dict):
                    raise VegaApiError("Invalid JSON response")
                return payload
        except (asyncio.TimeoutError, ClientError, ValueError) as err:
            raise VegaApiError(str(err)) from err

    async def state(self) -> dict[str, Any]:
        state = await self._request("GET", "/api/ha/state")
        if not all(key in state for key in ("enabled", "relay", "target", "sensor_ok")):
            raise VegaApiError("Unexpected firmware/API response. Install firmware v6.2.")
        return state

    async def mode(self, heat: bool) -> None:
        result = await self._request("POST", "/api/ha/mode", {"mode": "heat" if heat else "off"})
        if result.get("ok") is not True:
            raise VegaApiError("Mode command rejected")

    async def target(self, temperature: float) -> None:
        result = await self._request("POST", "/api/ha/target", {"target": f"{temperature:.1f}"})
        if result.get("ok") is not True:
            raise VegaApiError("Temperature command rejected")
