"""Polling coordinator for a single local ESP8266 thermostat."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VegaApiError, VegaLocalApi

_LOGGER = logging.getLogger(__name__)


class VegaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api: VegaLocalApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Vega-S Local",
            update_interval=timedelta(seconds=8),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.state()
        except VegaApiError as err:
            raise UpdateFailed(f"Could not read local thermostat: {err}") from err
