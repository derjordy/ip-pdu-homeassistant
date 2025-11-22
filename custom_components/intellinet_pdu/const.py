"""Constants for the Intellinet PDU integration."""

DOMAIN = "intellinet_pdu"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VOLTAGE = "voltage"

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_VOLTAGE = 230

# Voltage options for power calculation (Watt = Volt * Ampere)
VOLTAGE_OPTIONS = {
    "230": 230,  # Europe, Australia, most of Asia, Africa, South America
    "220": 220,  # Some countries in Europe, Asia
    "240": 240,  # UK, Australia
    "120": 120,  # USA, Canada, Mexico, Japan (some regions)
    "110": 110,  # Japan (some regions), Taiwan
    "100": 100,  # Japan (some regions)
}

# Update interval in seconds
SCAN_INTERVAL = 30
