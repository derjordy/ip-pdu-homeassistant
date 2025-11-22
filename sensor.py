"""Sensor platform for Intellinet PDU."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfTemperature,
)
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
    """Set up Intellinet PDU sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_info = data["device_info"]
    voltage = data["voltage"]

    sensors = [
        IntellinetPDUTemperatureSensor(coordinator, entry.entry_id, device_info),
        IntellinetPDUHumiditySensor(coordinator, entry.entry_id, device_info),
        IntellinetPDUCurrentSensor(coordinator, entry.entry_id, device_info),
        IntellinetPDUPowerSensor(coordinator, entry.entry_id, device_info, voltage),
    ]

    async_add_entities(sensors)


class IntellinetPDUBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Intellinet PDU sensors."""

    def __init__(self, coordinator, entry_id: str, device_info: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._device_info = device_info

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


class IntellinetPDUTemperatureSensor(IntellinetPDUBaseSensor):
    """Temperature sensor for Intellinet PDU."""

    def __init__(self, coordinator, entry_id: str, device_info: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_info)
        self._attr_unique_id = f"{entry_id}_temperature"
        self._attr_name = "PDU Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> float | None:
        """Return the temperature."""
        status = self.coordinator.data.get("status", {})
        temp = status.get("degree_celcius")
        if temp is not None:
            try:
                return float(temp)
            except ValueError:
                return None
        return None


class IntellinetPDUHumiditySensor(IntellinetPDUBaseSensor):
    """Humidity sensor for Intellinet PDU."""

    def __init__(self, coordinator, entry_id: str, device_info: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_info)
        self._attr_unique_id = f"{entry_id}_humidity"
        self._attr_name = "PDU Humidity"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> float | None:
        """Return the humidity."""
        status = self.coordinator.data.get("status", {})
        humidity = status.get("humidity_percent")
        if humidity is not None:
            try:
                return float(humidity)
            except ValueError:
                return None
        return None


class IntellinetPDUCurrentSensor(IntellinetPDUBaseSensor):
    """Current sensor for Intellinet PDU."""

    def __init__(self, coordinator, entry_id: str, device_info: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_info)
        self._attr_unique_id = f"{entry_id}_current"
        self._attr_name = "PDU Current"
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def native_value(self) -> float | None:
        """Return the current in amperes."""
        status = self.coordinator.data.get("status", {})
        current = status.get("current_amperes")
        if current is not None:
            try:
                return float(current)
            except ValueError:
                return None
        return None


class IntellinetPDUPowerSensor(IntellinetPDUBaseSensor):
    """Power sensor for Intellinet PDU (calculated from current * configured voltage)."""

    def __init__(self, coordinator, entry_id: str, device_info: dict, voltage: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_info)
        self._voltage = voltage
        self._attr_unique_id = f"{entry_id}_power"
        self._attr_name = "PDU Power"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_icon = "mdi:flash"

    @property
    def native_value(self) -> float | None:
        """Return the power in watts (current * configured voltage)."""
        status = self.coordinator.data.get("status", {})
        current = status.get("current_amperes")
        if current is not None:
            try:
                return round(float(current) * self._voltage, 1)
            except ValueError:
                return None
        return None
