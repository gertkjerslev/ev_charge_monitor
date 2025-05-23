from homeassistant.core import HomeAssistant
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.warning("EV Charge Monitor custom component was loaded.")
    return True
