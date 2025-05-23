# EV Charge Monitor

## Config
Put the following configuration in your `configuration.yaml`:

sensor:
  - platform: ev_charge_monitor
    charger_entity: sensor.ev_charger_v2
    price_entity: sensor.energi_data_service
    refund_enabled: true
    refund_rate: 0.87
    monthly_subscription: 24


