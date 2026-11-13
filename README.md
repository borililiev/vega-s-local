# Vega-S Local Thermostat (Home Assistant / HACS)

A local Home Assistant `climate` integration for the **Vega-S 400** thermostat running ESP8266 firmware **v6.2 HA Local**.

- No MQTT, no cloud.
- Existing ESP8266 web interface continues to work.
- Exposes a standard **climate** entity with OFF / HEAT, target temperature, measured temperature and relay state.
- Communicates with ESP8266 using `http://<controller-ip>/api/ha/state` and `POST` commands.

## Requirements

1. Install and run firmware **Vega_S_400_Local_v6_2.ino** on the ESP8266 (from the separate firmware ZIP).
2. Confirm `http://<controller-ip>/health` returns `Heater Performance v6.2 HA Local alive`.
3. Home Assistant and ESP8266 must be reachable on the same network (or routed local networks).
4. HACS installed in Home Assistant.

## Install via HACS (custom repository)

1. Create a GitHub repository called `vega-s-local` and upload this repository's **contents** to its root (`custom_components/vega_s_local`, `hacs.json`, `README.md`). Do **not** upload the ZIP alone.
2. In HACS, open the three-dot menu → **Custom repositories**.
3. Enter `https://github.com/<YOUR_GITHUB_USERNAME>/vega-s-local` and select category **Integration**.
4. Add the repository, find **Vega-S Local Thermostat**, and select **Download**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration** → **Vega-S Local Thermostat**.
7. Enter the controller's LAN address (for example `192.168.1.97`, without `http://`).
8. Add the `climate` entity to a standard **Thermostat** card.

## API

- `GET /api/ha/state`
- `POST /api/ha/mode` with form field `mode=heat|off`
- `POST /api/ha/target` with form field `target=22.0`

Commands are evaluated by the ESP8266 thermostat's own safety and sensor checks. Disabling heating is always allowed.

## Security

The HTTP API is unauthenticated. Keep the device and Home Assistant on a trusted LAN; do not expose the ESP8266 to the Internet.

## Troubleshooting

If the integration reports `cannot_connect`, confirm the ESP8266 runs **v6.2**, is reachable from the Home Assistant Docker container, and `/api/ha/state` returns valid JSON. A successful web page alone is not enough: the API endpoints must exist.

This is a community integration, not an official Home Assistant integration. Physical device and Home Assistant tests are required.
