from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up ClickPi Garage Door from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["cover"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a ClickPi Garage Door config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "cover")
