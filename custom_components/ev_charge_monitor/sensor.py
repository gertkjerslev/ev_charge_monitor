from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_DANISH_KRONE
from .const import DOMAIN

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    charger_entity = config.get("charger_entity")
    price_entity = config.get("price_entity")
    refund_enabled = config.get("refund_enabled", False)
    refund_rate = config.get("refund_rate", 0.87)
    monthly_sub = config.get("monthly_subscription", 79)

    async_add_entities([
        EVChargeSensor(hass, charger_entity, price_entity, refund_enabled, refund_rate, monthly_sub)
    ])

class EVChargeSensor(SensorEntity):
    def __init__(self, hass, charger_entity, price_entity, refund_enabled, refund_rate, monthly_sub):
        self._hass = hass
        self._charger_entity = charger_entity
        self._price_entity = price_entity
        self._refund_enabled = refund_enabled
        self._refund_rate = refund_rate
        self._monthly_sub = monthly_sub
        self._attr_name = "EV Charge Price"
        self._attr_unit_of_measurement = CURRENCY_DANISH_KRONE
        self._state = None

    async def async_update(self):
        charger_state = self._hass.states.get(self._charger_entity)
        price_state = self._hass.states.get(self._price_entity)

        if charger_state is None or price_state is None:
            self._state = None
            return

        try:
            kwh = float(charger_state.state)
            spot_price = float(price_state.state)
        except ValueError:
            self._state = None
            return

        cost = kwh * spot_price

        if self._refund_enabled:
            refund = kwh * self._refund_rate
            cost -= refund
            cost += self._monthly_sub / 30  # daglig abonnementsandel

        self._state = round(cost, 2)
