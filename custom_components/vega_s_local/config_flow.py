"""UI setup for the local Vega-S ESP8266 climate integration."""
from __future__ import annotations

import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VegaApiError, VegaLocalApi
from .const import CONF_HOST, DOMAIN

# Literal LAN IPv4 or a safe LAN hostname (no scheme/path/port).
_HOST_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.-]{0,124}[a-zA-Z0-9]$")


class VegaLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            if not _HOST_RE.fullmatch(host) or ".." in host:
                errors[CONF_HOST] = "invalid_host"
            else:
                try:
                    api = VegaLocalApi(async_get_clientsession(self.hass), host)
                    await api.state()
                except VegaApiError:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Vega-S 400 ({host})", data={CONF_HOST: host}
                    )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
