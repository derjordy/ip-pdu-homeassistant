"""The Intellinet PDU integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IPU
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_VOLTAGE,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_VOLTAGE,
    VOLTAGE_OPTIONS,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intellinet PDU from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data.get(CONF_USERNAME, DEFAULT_USERNAME)
    password = entry.data.get(CONF_PASSWORD, DEFAULT_PASSWORD)
    voltage_key = entry.data.get(CONF_VOLTAGE, str(DEFAULT_VOLTAGE))
    voltage = VOLTAGE_OPTIONS.get(voltage_key, DEFAULT_VOLTAGE)

    pdu = IPU(host, auth=(username, password))

    # Fetch device info once at setup (doesn't change often)
    device_info = await hass.async_add_executor_job(pdu.info_system)

    async def async_update_data():
        """Fetch data from PDU."""
        try:
            status = await hass.async_add_executor_job(pdu.status)
            pdu_config = await hass.async_add_executor_job(pdu.pdu_config)
            return {
                "status": status,
                "pdu_config": pdu_config,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with PDU: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "pdu": pdu,
        "device_info": device_info,
        "voltage": voltage,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
