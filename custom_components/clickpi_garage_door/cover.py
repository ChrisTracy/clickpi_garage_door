import aiohttp
import logging

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from .const import CUSTOMTRIGGER_ENDPOINT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the ClickPi Garage Door cover entity."""
    config = entry.data
    host = config["host"].rstrip("/")
    api_key = config["api_key"]
    pin = config["pin_number"]
    sensor = config["sensor"]
    name = config.get("name", "Garage door")

    async_add_entities([ClickPiCover(hass, name, host, api_key, pin, sensor)])

class ClickPiCover(CoverEntity):
    """Representation of a ClickPi Garage Door cover."""

    def __init__(self, hass, name, host, api_key, pin, sensor):
        self.hass = hass
        self._name = name
        self._host = host
        self._api_key = api_key
        self._pin = pin
        self._sensor = sensor
        self._attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    @property
    def name(self):
        return self._name
    
    @property
    def unique_id(self):
        return f"{self._host}-{self._pin}"

    @property
    def is_closed(self):
        """Return True if cover is closed based on sensor state."""
        sensor_state = self.hass.states.get(self._sensor)
        if sensor_state:
            if sensor_state.state.lower() in ["on", "open"]:
                return False
            elif sensor_state.state.lower() in ["off", "closed"]:
                return True
        return None
    
    @property
    def device_info(self):
        """Return device information for device registry."""
        return {
            "identifiers": {("clickpi_garage_door", self._host)},
            "name": self._name,
            "manufacturer": "ClickPi",
            "model": "Garage Door Controller",
        }

    async def async_open_cover(self, **kwargs):
        """Open the garage door."""
        await self._trigger_cover()

    async def async_close_cover(self, **kwargs):
        """Close the garage door."""
        await self._trigger_cover()

    async def _trigger_cover(self):
        """Trigger the cover action via POST request."""
        url = f"{self._host}{CUSTOMTRIGGER_ENDPOINT}?pin={self._pin}"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            session = aiohttp.ClientSession()
            async with session.post(url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to trigger cover, status: %s", response.status)
        except Exception as err:
            _LOGGER.exception("Error triggering cover: %s", err)
        finally:
            await session.close()

    async def async_added_to_hass(self):
        """Subscribe to sensor state changes."""
        from homeassistant.helpers.event import async_track_state_change_event
        async_track_state_change_event(self.hass, self._sensor, self._sensor_changed_event)


    def _sensor_changed_event(self, event):
        """Handle sensor state change event."""
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        self.async_write_ha_state()

