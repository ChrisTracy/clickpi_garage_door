from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.event import async_track_state_change

from .const import CUSTOMTRIGGER_ENDPOINT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
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

    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, name: str, host: str, api_key: str, pin: int, sensor: str):
        self.hass = hass
        self._name = name
        self._host = host
        self._api_key = api_key
        self._pin = pin
        self._sensor = sensor
        self._attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        self._attr_is_closed: bool | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f"{self._host}-{self._pin}"

    @property
    def is_closed(self) -> bool | None:
        """Return True if cover is closed based on sensor state."""
        sensor_state = self.hass.states.get(self._sensor)
        if not sensor_state:
            return None

        s = sensor_state.state.lower()
        # Many contact sensors: ON=open, OFF=closed
        if s in ("on", "open", STATE_ON):
            return False
        if s in ("off", "closed", STATE_OFF):
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

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the garage door."""
        await self._trigger_cover()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the garage door."""
        await self._trigger_cover()

    async def _trigger_cover(self) -> None:
        """Trigger the cover action via POST request."""
        endpoint = CUSTOMTRIGGER_ENDPOINT if CUSTOMTRIGGER_ENDPOINT.startswith("/") else f"/{CUSTOMTRIGGER_ENDPOINT}"
        url = f"{self._host}{endpoint}?pin={self._pin}"
        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            async with session.post(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to trigger cover, status: %s", resp.status)
        except Exception as err:
            _LOGGER.exception("Error triggering cover: %s", err)

    async def async_added_to_hass(self) -> None:
        """Subscribe to sensor state changes."""
        # Initialize state immediately
        st = self.hass.states.get(self._sensor)
        self._apply_sensor_state(st.state if st else None)
        # Subscribe; this delivers (entity_id, old_state, new_state) on the HA loop
        async_track_state_change(self.hass, [self._sensor], self._async_sensor_changed)

    @callback
    def _async_sensor_changed(self, entity_id, old_state, new_state) -> None:
        """Handle sensor state change safely on HA event loop."""
        self._apply_sensor_state(new_state.state if new_state else None)
        # Thread-safe way to push a state write
        self.schedule_update_ha_state()

    def _apply_sensor_state(self, state: str | None) -> None:
        if state is None:
            self._attr_is_closed = None
            return
        s = state.lower()
        if s in ("on", "open", STATE_ON):
            self._attr_is_closed = False
        elif s in ("off", "closed", STATE_OFF):
            self._attr_is_closed = True
        else:
            self._attr_is_closed = None
