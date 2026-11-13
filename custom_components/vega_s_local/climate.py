"""Standard Home Assistant climate entity for the local Vega-S thermostat."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_TEMPERATURE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import VegaApiError
from .const import CONF_HOST, DOMAIN
from .coordinator import VegaCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([VegaClimate(hass.data[DOMAIN][entry.entry_id], entry)])


class VegaClimate(CoordinatorEntity[VegaCoordinator], ClimateEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    # HA 2026.11+ requires native_temperature_unit for native_* temperature fields.
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 12.0
    _attr_max_temp = 28.0

    def __init__(self, coordinator: VegaCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        host = entry.data[CONF_HOST]
        self._attr_unique_id = f"vega_s_local_{host.lower().replace('.', '_')}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host.lower())},
            manufacturer="Vega-S / ESP8266",
            model="Vega-S 400 thermostat",
            name="Отопление Vega-S 400",
            configuration_url=f"http://{host}/",
        )

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.HEAT if self.coordinator.data.get("enabled") else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        data = self.coordinator.data
        if data.get("relay"):
            return HVACAction.HEATING
        if data.get("enabled") and not data.get("locked"):
            return HVACAction.IDLE
        return HVACAction.OFF

    @property
    def native_current_temperature(self) -> float | None:
        data = self.coordinator.data
        if data.get("sensor_ok") is not True:
            return None
        try:
            return float(data["temperature"])
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def native_target_temperature(self) -> float | None:
        try:
            return float(self.coordinator.data["target"])
        except (KeyError, TypeError, ValueError):
            return None

    # For Home Assistant versions before 2026.11, the temperature fields used
    # legacy names. Define those ONLY on older versions to avoid deprecation
    # warnings on HA 2026.11+.
    if not hasattr(ClimateEntity, "native_temperature_unit"):

        @property
        def temperature_unit(self) -> str:
            return UnitOfTemperature.CELSIUS

        @property
        def current_temperature(self) -> float | None:
            return self.native_current_temperature

        @property
        def target_temperature(self) -> float | None:
            return self.native_target_temperature

    @property
    def current_humidity(self) -> float | None:
        data = self.coordinator.data
        return float(data["humidity"]) if data.get("sensor_ok") else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "relay_on": bool(data.get("relay")),
            "safety_lock": bool(data.get("locked")),
            "manual_override": bool(data.get("manual")),
            "sensor_ok": bool(data.get("sensor_ok")),
            "minimum_on_minutes": data.get("min_on_minutes"),
            "minimum_off_minutes": data.get("min_off_minutes"),
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode not in self._attr_hvac_modes:
            raise HomeAssistantError("Unsupported heating mode")
        try:
            await self.coordinator.api.mode(hvac_mode == HVACMode.HEAT)
        except VegaApiError as err:
            raise HomeAssistantError(f"Thermostat rejected mode: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Enable automatic heat using the ESP's own thermostat/safety rules."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Immediately disable heating on the device."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(kwargs[ATTR_TEMPERATURE])
        if not self._attr_min_temp <= temperature <= self._attr_max_temp:
            raise HomeAssistantError("Temperature must be between 12 and 28 °C")
        try:
            await self.coordinator.api.target(temperature)
        except VegaApiError as err:
            raise HomeAssistantError(f"Thermostat rejected temperature: {err}") from err
        await self.coordinator.async_request_refresh()
