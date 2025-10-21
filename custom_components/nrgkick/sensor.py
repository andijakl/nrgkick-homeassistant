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
            key="rated_current",
            name="Rated Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["info", "general", "rated_current"],
            precision=2,
        ),
        # INFO - Connector
        NRGkickSensor(
            coordinator,
            key="connector_phase_count",
            name="Connector Phase Count",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "connector", "phase_count"],
        ),
        NRGkickSensor(
            coordinator,
            key="connector_max_current",
            name="Connector Max Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["info", "connector", "max_current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="connector_type",
            name="Connector Type",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "connector", "type"],
        ),
        NRGkickSensor(
            coordinator,
            key="connector_serial",
            name="Connector Serial",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "connector", "serial"],
        ),
        # INFO - Grid
        NRGkickSensor(
            coordinator,
            key="grid_voltage",
            name="Grid Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["info", "grid", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="grid_frequency",
            name="Grid Frequency",
            unit=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["info", "grid", "frequency"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="grid_phases",
            name="Grid Phases",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "grid", "phases"],
        ),
        # INFO - Network
        NRGkickSensor(
            coordinator,
            key="network_ip_address",
            name="IP Address",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "network", "ip_address"],
        ),
        NRGkickSensor(
            coordinator,
            key="network_mac_address",
            name="MAC Address",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "network", "mac_address"],
        ),
        NRGkickSensor(
            coordinator,
            key="network_ssid",
            name="WiFi SSID",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "network", "ssid"],
        ),
        NRGkickSensor(
            coordinator,
            key="network_rssi",
            name="WiFi Signal Strength",
            unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["info", "network", "rssi"],
        ),
        # INFO - Versions
        NRGkickSensor(
            coordinator,
            key="versions_sw_sm",
            name="Software Version SM",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "versions", "sw_sm"],
            enabled_default=False,
        ),
        NRGkickSensor(
            coordinator,
            key="versions_hw_sm",
            name="Hardware Version SM",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["info", "versions", "hw_sm"],
            enabled_default=False,
        ),
        # Control
        NRGkickSensor(
            coordinator,
            key="current_set",
            name="Set Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["control", "current_set"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="charge_pause",
            name="Charge Pause",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["control", "charge_pause"],
        ),
        NRGkickSensor(
            coordinator,
            key="energy_limit",
            name="Energy Limit",
            unit=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            value_path=["control", "energy_limit"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        NRGkickSensor(
            coordinator,
            key="phase_count",
            name="Phase Count",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["control", "phase_count"],
        ),
        # VALUES - Energy
        NRGkickSensor(
            coordinator,
            key="total_charged_energy",
            name="Total Charged Energy",
            unit=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_path=["values", "energy", "total_charged_energy"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        NRGkickSensor(
            coordinator,
            key="charged_energy",
            name="Current Session Energy",
            unit=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_path=["values", "energy", "charged_energy"],
            precision=3,
            suggested_unit=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        # VALUES - Powerflow (Total)
        NRGkickSensor(
            coordinator,
            key="charging_voltage",
            name="Charging Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "charging_voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="charging_current",
            name="Charging Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "charging_current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="powerflow_grid_frequency",
            name="Powerflow Grid Frequency",
            unit=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "grid_frequency"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="peak_power",
            name="Peak Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "peak_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="total_active_power",
            name="Total Active Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "total_active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="total_reactive_power",
            name="Total Reactive Power",
            unit=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "total_reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="total_apparent_power",
            name="Total Apparent Power",
            unit=UnitOfApparentPower.VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "total_apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="total_power_factor",
            name="Total Power Factor",
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "total_power_factor"],
        ),
        # VALUES - Powerflow L1
        NRGkickSensor(
            coordinator,
            key="l1_voltage",
            name="L1 Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l1_current",
            name="L1 Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l1_active_power",
            name="L1 Active Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l1_reactive_power",
            name="L1 Reactive Power",
            unit=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l1_apparent_power",
            name="L1 Apparent Power",
            unit=UnitOfApparentPower.VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l1_power_factor",
            name="L1 Power Factor",
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l1", "power_factor"],
        ),
        # VALUES - Powerflow L2
        NRGkickSensor(
            coordinator,
            key="l2_voltage",
            name="L2 Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l2_current",
            name="L2 Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l2_active_power",
            name="L2 Active Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l2_reactive_power",
            name="L2 Reactive Power",
            unit=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l2_apparent_power",
            name="L2 Apparent Power",
            unit=UnitOfApparentPower.VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l2_power_factor",
            name="L2 Power Factor",
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l2", "power_factor"],
        ),
        # VALUES - Powerflow L3
        NRGkickSensor(
            coordinator,
            key="l3_voltage",
            name="L3 Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "voltage"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l3_current",
            name="L3 Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "current"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l3_active_power",
            name="L3 Active Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "active_power"],
            precision=2,
        ),
        NRGkickSensor(
            coordinator,
            key="l3_reactive_power",
            name="L3 Reactive Power",
            unit=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "reactive_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l3_apparent_power",
            name="L3 Apparent Power",
            unit=UnitOfApparentPower.VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "apparent_power"],
        ),
        NRGkickSensor(
            coordinator,
            key="l3_power_factor",
            name="L3 Power Factor",
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "l3", "power_factor"],
        ),
        # VALUES - Powerflow Neutral
        NRGkickSensor(
            coordinator,
            key="n_current",
            name="Neutral Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "powerflow", "n", "current"],
            precision=2,
        ),
        # VALUES - General
        NRGkickSensor(
            coordinator,
            key="charging_rate",
            name="Charging Rate",
            unit=None,
            device_class=None,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "general", "charging_rate"],
        ),
        NRGkickSensor(
            coordinator,
            key="vehicle_connect_time",
            name="Vehicle Connect Time",
            unit=UnitOfTime.SECONDS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "general", "vehicle_connect_time"],
        ),
        NRGkickSensor(
            coordinator,
            key="vehicle_charging_time",
            name="Vehicle Charging Time",
            unit=UnitOfTime.SECONDS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "general", "vehicle_charging_time"],
        ),
        NRGkickSensor(
            coordinator,
            key="status",
            name="Charging Status",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "status"],
            value_fn=lambda x: (
                STATUS_MAP.get(
                    x,
                    "Unknown",
                )
                if isinstance(x, int)
                else x
            ),
        ),
        NRGkickSensor(
            coordinator,
            key="charge_permitted",
            name="Charge Permitted",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "charge_permitted"],
        ),
        NRGkickSensor(
            coordinator,
            key="relay_state",
            name="Relay State",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "relay_state"],
        ),
        NRGkickSensor(
            coordinator,
            key="charge_count",
            name="Charge Count",
            unit=None,
            device_class=None,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_path=["values", "general", "charge_count"],
        ),
        NRGkickSensor(
            coordinator,
            key="rcd_trigger",
            name="RCD Trigger",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "rcd_trigger"],
        ),
        NRGkickSensor(
            coordinator,
            key="warning_code",
            name="Warning Code",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "warning_code"],
        ),
        NRGkickSensor(
            coordinator,
            key="error_code",
            name="Error Code",
            unit=None,
            device_class=None,
            state_class=None,
            value_path=["values", "general", "error_code"],
        ),
        # VALUES - Temperatures
        NRGkickSensor(
            coordinator,
            key="housing_temperature",
            name="Housing Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "housing"],
        ),
        NRGkickSensor(
            coordinator,
            key="connector_l1_temperature",
            name="Connector L1 Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "connector_l1"],
        ),
        NRGkickSensor(
            coordinator,
            key="connector_l2_temperature",
            name="Connector L2 Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "connector_l2"],
        ),
        NRGkickSensor(
            coordinator,
            key="connector_l3_temperature",
            name="Connector L3 Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "connector_l3"],
        ),
        NRGkickSensor(
            coordinator,
            key="domestic_plug_1_temperature",
            name="Domestic Plug 1 Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "domestic_plug_1"],
        ),
        NRGkickSensor(
            coordinator,
            key="domestic_plug_2_temperature",
            name="Domestic Plug 2 Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_path=["values", "temperatures", "domestic_plug_2"],
        ),
    ]

    async_add_entities(entities)


class NRGkickSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NRGkick sensor."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        *,
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
