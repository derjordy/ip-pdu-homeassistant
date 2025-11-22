"""Switch platform for Intellinet PDU."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Intellinet PDU switches."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    pdu = data["pdu"]
    device_info = data["device_info"]

    switches = []
    for outlet_id in range(8):
        switches.append(
            IntellinetPDUSwitch(
                coordinator,
                pdu,
                outlet_id,
                entry.entry_id,
                device_info,
            )
        )

    async_add_entities(switches)


class IntellinetPDUSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Intellinet PDU outlet switch."""

    def __init__(self, coordinator, pdu, outlet_id: int, entry_id: str, device_info: dict) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._pdu = pdu
        self._outlet_id = outlet_id
        self._entry_id = entry_id
        self._device_info = device_info

        self._attr_unique_id = f"{entry_id}_outlet_{outlet_id}"
        self._update_attributes()

    def _update_attributes(self) -> None:
        """Update entity attributes from coordinator data."""
        pdu_config = self.coordinator.data.get("pdu_config", {})
        outlet_config = pdu_config.get(f"outlet{self._outlet_id}", {})
        outlet_name = outlet_config.get("name", "")

        # Format: "Steckdose 1: Name" or just "Steckdose 1" if no name
        outlet_number = self._outlet_id + 1
        if outlet_name:
            self._attr_name = f"Steckdose {outlet_number}: {outlet_name}"
        else:
            self._attr_name = f"Steckdose {outlet_number}"

        self._attr_icon = "mdi:power-socket-de"

    @property
    def is_on(self) -> bool:
        """Return true if the outlet is on."""
        status = self.coordinator.data.get("status", {})
        outlet_states = status.get("outlet_states", [])
        if self._outlet_id < len(outlet_states):
            return outlet_states[self._outlet_id] == "on"
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attributes()
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the outlet on."""
        await self.hass.async_add_executor_job(
            self._pdu.enable_outlets, [self._outlet_id]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the outlet off."""
        await self.hass.async_add_executor_job(
            self._pdu.disable_outlets, [self._outlet_id]
        )
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_info.get("mac_address", self._entry_id))},
            "name": self._device_info.get("system_name", "IP PDU"),
            "manufacturer": "Generic",
            "model": self._device_info.get("product_model", "IP PDU"),
            "sw_version": self._device_info.get("firmware_version"),
        }
