import requests
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, CURRENCY_DANISH_KRONE
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    charger_entity = config.get("charger_entity")
    refund_enabled = config.get("refund_enabled", False)
    refund_rate = config.get("refund_rate", 0.87)
    monthly_sub = config.get("monthly_subscription", 79)

    async_add_entities([
        EVChargeSensor(hass, charger_entity, refund_enabled, refund_rate, monthly_sub)
    ])

class EVChargeSensor(SensorEntity):
    def __init__(self, hass, charger_entity, refund_enabled, refund_rate, monthly_sub):
        self._hass = hass
        self._charger_entity = charger_entity
        self._refund_enabled = refund_enabled
        self._refund_rate = refund_rate
        self._monthly_sub = monthly_sub
        self._attr_name = "EV Charge Price"
        self._attr_unit_of_measurement = CURRENCY_DANISH_KRONE
        self._state = None

    def fetch_current_price(self):
        now = datetime.now().strftime('%Y-%m-%dT%H:00')
        url = f"https://api.energidataservice.dk/dataset/Elspotprices?offset=0&limit=1&filter={{\"HourDK\":\"{now}\",\"PriceArea\":\"DK1\"}}&sort=HourDK DESC"
        try:
            res = requests.get(url)
            res.raise_for_status()
            price_øre = res.json()["records"][0]["SpotPriceDKK"]
            return price_øre / 100.0
        except Exception:
            return 2.0  # fallback spotpris

    async def async_update(self):
        charger_state = self._hass.states.get(self._charger_entity)
        if charger_state is None:
            self._state = None
            return

        try:
            kwh = float(charger_state.state)
        except ValueError:
            self._state = None
            return

        price_per_kwh = self.fetch_current_price()
        price = kwh * price_per_kwh

        if self._refund_enabled:
            refund = kwh * self._refund_rate
            price -= refund
            price += self._monthly_sub / 30  # dagsabonnement

        self._state = round(price, 2)
