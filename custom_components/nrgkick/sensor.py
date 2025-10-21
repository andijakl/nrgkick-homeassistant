"""Sensor platform for NRGkick."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NRGkickDataUpdateCoordinator
from .const import DOMAIN, STATUS_MAP


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NRGkick sensors based on a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NRGkickSensor] = [
        # INFO - General
        NRGkickSensor(
            coordinator,
            "rated_current",
            "Rated Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["info", "general", "rated_current"],
            precision=2,
        ),
        # INFO - Connector
        NRGkickSensor(
            coordinator,
            "connector_phase_count",
            "Connector Phase Count",
            None,
            None,
            None,
            ["info", "connector", "phase_count"],
        ),
        NRGkickSensor(
            coordinator,
            "connector_max_current",
            "Connector Max Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["info", "connector", "max_current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "connector_type",
            "Connector Type",
            None,
            None,
            None,
            ["info", "connector", "type"],
        ),
        NRGkickSensor(
            coordinator,
            "connector_serial",
            "Connector Serial",
            None,
            None,
            None,
            ["info", "connector", "serial"],
        ),
        # INFO - Grid
        NRGkickSensor(
            coordinator,
            "grid_voltage",
            "Grid Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            ["info", "grid", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "grid_frequency",
            "Grid Frequency",
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
            ["info", "grid", "frequency"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "grid_phases",
            "Grid Phases",
            None,
            None,
            None,
            ["info", "grid", "phases"],
        ),
        # INFO - Network
        NRGkickSensor(
            coordinator,
            "network_ip_address",
            "IP Address",
            None,
            None,
            None,
            ["info", "network", "ip_address"],
        ),
        NRGkickSensor(
            coordinator,
            "network_mac_address",
            "MAC Address",
            None,
            None,
            None,
            ["info", "network", "mac_address"],
        ),
        NRGkickSensor(
            coordinator,
            "network_ssid",
            "WiFi SSID",
            None,
            None,
            None,
            ["info", "network", "ssid"],
        ),
        NRGkickSensor(
            coordinator,
            "network_rssi",
            "WiFi Signal Strength",
            SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            SensorDeviceClass.SIGNAL_STRENGTH,
            SensorStateClass.MEASUREMENT,
            ["info", "network", "rssi"],
        ),
        # INFO - Versions
        NRGkickSensor(
            coordinator,
            "versions_sw_sm",
            "Software Version SM",
            None,
            None,
            None,
            ["info", "versions", "sw_sm"],
            enabled_default=False,
        ),
        NRGkickSensor(
            coordinator,
            "versions_hw_sm",
            "Hardware Version SM",
            None,
            None,
            None,
            ["info", "versions", "hw_sm"],
            enabled_default=False,
        ),
        # Control
        NRGkickSensor(
            coordinator,
            "current_set",
            "Set Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["control", "current_set"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "charge_pause",
            "Charge Pause",
            None,
            None,
            None,
            ["control", "charge_pause"],
        ),
        NRGkickSensor(
            coordinator,
            "energy_limit",
            "Energy Limit",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL,
            ["control", "energy_limit"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        NRGkickSensor(
            coordinator,
            "phase_count",
            "Phase Count",
            None,
            None,
            None,
            ["control", "phase_count"],
        ),
        # VALUES - Energy
        NRGkickSensor(
            coordinator,
            "total_charged_energy",
            "Total Charged Energy",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
            ["values", "energy", "total_charged_energy"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        NRGkickSensor(
            coordinator,
            "charged_energy",
            "Current Session Energy",
            UnitOfEnergy.WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
            ["values", "energy", "charged_energy"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        # VALUES - Powerflow (Total)
        NRGkickSensor(
            coordinator,
            "charging_voltage",
            "Charging Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "charging_voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "charging_current",
            "Charging Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "charging_current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "powerflow_grid_frequency",
            "Powerflow Grid Frequency",
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "grid_frequency"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "peak_power",
            "Peak Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "peak_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "total_active_power",
            "Total Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "total_active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "total_reactive_power",
            "Total Reactive Power",
            UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            SensorDeviceClass.REACTIVE_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "total_reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            "total_apparent_power",
            "Total Apparent Power",
            UnitOfApparentPower.VOLT_AMPERE,
            SensorDeviceClass.APPARENT_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "total_apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            "total_power_factor",
            "Total Power Factor",
            PERCENTAGE,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "total_power_factor"],
        ),
        # VALUES - Powerflow L1
        NRGkickSensor(
            coordinator,
            "l1_voltage",
            "L1 Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l1_current",
            "L1 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l1_active_power",
            "L1 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l1_reactive_power",
            "L1 Reactive Power",
            UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            SensorDeviceClass.REACTIVE_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l1_apparent_power",
            "L1 Apparent Power",
            UnitOfApparentPower.VOLT_AMPERE,
            SensorDeviceClass.APPARENT_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l1_power_factor",
            "L1 Power Factor",
            PERCENTAGE,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l1", "power_factor"],
        ),
        # VALUES - Powerflow L2
        NRGkickSensor(
            coordinator,
            "l2_voltage",
            "L2 Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l2_current",
            "L2 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l2_active_power",
            "L2 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l2_reactive_power",
            "L2 Reactive Power",
            UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            SensorDeviceClass.REACTIVE_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l2_apparent_power",
            "L2 Apparent Power",
            UnitOfApparentPower.VOLT_AMPERE,
            SensorDeviceClass.APPARENT_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l2_power_factor",
            "L2 Power Factor",
            PERCENTAGE,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l2", "power_factor"],
        ),
        # VALUES - Powerflow L3
        NRGkickSensor(
            coordinator,
            "l3_voltage",
            "L3 Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l3_current",
            "L3 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l3_active_power",
            "L3 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            "l3_reactive_power",
            "L3 Reactive Power",
            UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            SensorDeviceClass.REACTIVE_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l3_apparent_power",
            "L3 Apparent Power",
            UnitOfApparentPower.VOLT_AMPERE,
            SensorDeviceClass.APPARENT_POWER,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            "l3_power_factor",
            "L3 Power Factor",
            PERCENTAGE,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "l3", "power_factor"],
        ),
        # VALUES - Powerflow Neutral
        NRGkickSensor(
            coordinator,
            "n_current",
            "Neutral Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
            ["values", "powerflow", "n", "current"],
            precision=2,
        ),
        # VALUES - General
        NRGkickSensor(
            coordinator,
            "charging_rate",
            "Charging Rate",
            None,
            None,
            SensorStateClass.MEASUREMENT,
            ["values", "general", "charging_rate"],
        ),
        NRGkickSensor(
            coordinator,
            "vehicle_connect_time",
            "Vehicle Connect Time",
            UnitOfTime.SECONDS,
            SensorDeviceClass.DURATION,
            SensorStateClass.MEASUREMENT,
            ["values", "general", "vehicle_connect_time"],
        ),
        NRGkickSensor(
            coordinator,
            "vehicle_charging_time",
            "Vehicle Charging Time",
            UnitOfTime.SECONDS,
            SensorDeviceClass.DURATION,
            SensorStateClass.MEASUREMENT,
            ["values", "general", "vehicle_charging_time"],
        ),
        NRGkickSensor(
            coordinator,
            "status",
            "Charging Status",
            None,
            None,
            None,
            ["values", "general", "status"],
            value_fn=lambda x: (
                STATUS_MAP.get(x, "Unknown") if isinstance(x, int) else x
            ),
        ),
        NRGkickSensor(
            coordinator,
            "charge_permitted",
            "Charge Permitted",
            None,
            None,
            None,
            ["values", "general", "charge_permitted"],
        ),
        NRGkickSensor(
            coordinator,
            "relay_state",
            "Relay State",
            None,
            None,
            None,
            ["values", "general", "relay_state"],
        ),
        NRGkickSensor(
            coordinator,
            "charge_count",
            "Charge Count",
            None,
            None,
            SensorStateClass.TOTAL_INCREASING,
            ["values", "general", "charge_count"],
        ),
        NRGkickSensor(
            coordinator,
            "rcd_trigger",
            "RCD Trigger",
            None,
            None,
            None,
            ["values", "general", "rcd_trigger"],
        ),
        NRGkickSensor(
            coordinator,
            "warning_code",
            "Warning Code",
            None,
            None,
            None,
            ["values", "general", "warning_code"],
        ),
        NRGkickSensor(
            coordinator,
            "error_code",
            "Error Code",
            None,
            None,
            None,
            ["values", "general", "error_code"],
        ),
        # VALUES - Temperatures
        NRGkickSensor(
            coordinator,
            "housing_temperature",
            "Housing Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "housing"],
        ),
        NRGkickSensor(
            coordinator,
            "connector_l1_temperature",
            "Connector L1 Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "connector_l1"],
        ),
        NRGkickSensor(
            coordinator,
            "connector_l2_temperature",
            "Connector L2 Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "connector_l2"],
        ),
        NRGkickSensor(
            coordinator,
            "connector_l3_temperature",
            "Connector L3 Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "connector_l3"],
        ),
        NRGkickSensor(
            coordinator,
            "domestic_plug_1_temperature",
            "Domestic Plug 1 Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "domestic_plug_1"],
        ),
        NRGkickSensor(
            coordinator,
            "domestic_plug_2_temperature",
            "Domestic Plug 2 Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            ["values", "temperatures", "domestic_plug_2"],
        ),
    ]

    async_add_entities(entities)


class NRGkickSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NRGkick sensor."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        value_path: list[str],
        value_fn: Any = None,
        precision: int | None = None,
        suggested_unit: str | None = None,
        enabled_default: bool = True,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"NRGkick {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._value_path = value_path
        self._value_fn = value_fn
        self._attr_entity_registry_enabled_default = enabled_default

        if precision is not None:
            self._attr_suggested_display_precision = precision
        if suggested_unit is not None:
            self._attr_suggested_unit_of_measurement = suggested_unit

        # Device info
        device_info = coordinator.data.get("info", {}).get("general", {})
        self._attr_unique_id = f"{device_info.get('serial_number', 'unknown')}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info.get("serial_number", "unknown"))},
            "name": device_info.get("device_name", "NRGkick"),
            "manufacturer": "DiniTech",
            "model": device_info.get("model_type", "NRGkick Gen2"),
            "sw_version": coordinator.data.get("info", {})
            .get("versions", {})
            .get("sw_sm"),
        }

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name and states."""
        return f"nrgkick_{self._key}"

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)

        if self._value_fn and data is not None:
            return self._value_fn(data)
        return data
