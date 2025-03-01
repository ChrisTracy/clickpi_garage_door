import aiohttp
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY
from .const import DOMAIN, DEFAULT_NAME, VERIFY_ENDPOINT

_LOGGER = logging.getLogger(__name__)

# Define the configuration schema for the integration
DATA_SCHEMA = vol.Schema({
    vol.Required("host"): str,
    vol.Required("api_key"): str,
    vol.Required("pin_number"): int,
    vol.Required("sensor"): str,
    vol.Optional("name", default=DEFAULT_NAME): str,
})

class ClickPiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ClickPi Garage Door."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input["host"].rstrip("/")
            api_key = user_input["api_key"]
            url = f"{host}{VERIFY_ENDPOINT}"
            headers = {"Authorization": f"Bearer {api_key}"}

            try:
                session = aiohttp.ClientSession()
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        errors["base"] = "cannot_connect"
                        _LOGGER.error("Verification failed, status code: %s", response.status)
            except Exception as err:
                _LOGGER.exception("Error connecting to ClickPi device: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await session.close()

            if not errors:
                return self.async_create_entry(title=user_input.get("name", DEFAULT_NAME), data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
