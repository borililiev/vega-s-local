# Vega-S Local Thermostat — HACS v1.1.0

Local Home Assistant `climate` integration for an ESP8266 Vega-S 400 thermostat running **firmware v6.2 HA Local**. No MQTT or cloud needed.

## Update v1.1.0 — thermostat temperature display fix

- Fixed temperature unit declaration to use `native_temperature_unit` in HA 2026.11+, matching `native_current_temperature` and `native_target_temperature`.
- Included fallback property names for older Home Assistant versions.
- Explicitly handle turn-on and turn-off actions.
- Expose sensor health and heating relay state in entity attributes.
- No ESP8266 firmware changes are needed **if v6.2 is already installed**.

## Updating through HACS

1. Upload all files from this repository ZIP to the **root** of your GitHub repository (preserve the `custom_components/vega_s_local/` directory).
2. In HACS find `Vega-S Local Thermostat` -> 3 dots -> **Update information**, then **Redownload** (or use the update notification).
3. Restart **Home Assistant**, not just the ESP8266.
4. Open **Developer Tools -> States** and find `climate.*vega*`. It should show `current_temperature`, `temperature` (setpoint), `temperature_unit`, and `hvac_action`.
5. Use the standard **Thermostat** card. If the card was created before the fix and still looks stale, refresh the Home Assistant UI in your browser.

## Required ESP firmware

The ESP8266 must respond to the following address:

`http://ESP_IP/api/ha/state`

Expected fields include `enabled`, `relay`, `sensor_ok`, `temperature`, `target`, and `humidity`. If `sensor_ok` is false, current temperature will be shown as unavailable until the sensor recovers. Do not bypass safety restrictions.

Temperature changes use `POST /api/ha/target`; modes use `POST /api/ha/mode`. The controller remains in charge of relay control and safety.

## Diagnostics

- `http://ESP_IP/health`: expect `Heater Performance v6.2 HA Local alive`.
- `http://ESP_IP/api/ha/state`: confirm `sensor_ok:true`, a plausible `temperature`, and `target`.
- Home Assistant: Developer Tools -> States -> your `climate` entity, check `current_temperature`, `temperature`, `temperature_unit`, `supported_features`.
- If the Home Assistant server is Docker, ensure it can reach `ESP_IP:80` from inside the container.

## Security

The local HTTP interface has no authentication. Keep the ESP8266 and Home Assistant on a trusted LAN; do not expose port 80 to the internet. The device's independent thermal protection and appropriate mains wiring are required for safe heater operation.
