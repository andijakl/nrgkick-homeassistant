"""Tests for the NRGkick sensor platform."""

from unittest.mock import patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant

from custom_components.nrgkick.const import STATUS_CHARGING


@pytest.fixture
def mock_values_data_sensor():
    """Mock values data for sensor tests."""
    return {
        "powerflow": {
            "total_active_power": 11000,
            "l1": {
                "voltage": 230.0,
                "current": 16.0,
                "active_power": 3680,
                "reactive_power": 0,
                "apparent_power": 3680,
                "power_factor": 100,
            },
            "l2": {
                "voltage": 230.0,
                "current": 16.0,
                "active_power": 3680,
                "reactive_power": 0,
                "apparent_power": 3680,
                "power_factor": 100,
            },
            "l3": {
                "voltage": 230.0,
                "current": 16.0,
                "active_power": 3680,
                "reactive_power": 0,
                "apparent_power": 3680,
                "power_factor": 100,
            },
            "charging_voltage": 230.0,
            "charging_current": 16.0,
            "grid_frequency": 50.0,
            "peak_power": 11000,
            "total_reactive_power": 0,
            "total_apparent_power": 11040,
            "total_power_factor": 100,
            "n": {"current": 0.0},
        },
        "general": {
            "status": STATUS_CHARGING,
            "charging_rate": 11.0,
            "vehicle_connect_time": 100,
            "vehicle_charging_time": 50,
            "charge_count": 5,
            "charge_permitted": True,
            "relay_state": True,
            "rcd_trigger": 0,
            "warning_code": 0,
            "error_code": 0,
        },
        "temperatures": {
            "housing": 35.0,
            "connector_l1": 28.0,
            "connector_l2": 29.0,
            "connector_l3": 28.5,
            "domestic_plug_1": 25.0,
            "domestic_plug_2": 25.0,
        },
        "energy": {
            "total_charged_energy": 100000,
            "charged_energy": 5000,
        },
    }


@pytest.mark.requires_integration
async def test_sensor_entities(
    hass: HomeAssistant,
    mock_config_entry,
    mock_nrgkick_api,
    mock_info_data,
    mock_control_data,
    mock_values_data_sensor,
) -> None:
    """Test sensor entities."""
    mock_config_entry.add_to_hass(hass)

    # Setup mock data
    mock_nrgkick_api.get_info.return_value = mock_info_data
    mock_nrgkick_api.get_control.return_value = mock_control_data
    mock_nrgkick_api.get_values.return_value = mock_values_data_sensor

    # Setup entry
    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Helper to get state by unique ID
    from homeassistant.helpers import entity_registry as er

    entity_registry = er.async_get(hass)

    def get_state_by_key(key):
        unique_id = f"TEST123456_{key}"
        entity_id = entity_registry.async_get_entity_id("sensor", "nrgkick", unique_id)
        if not entity_id:
            return None
        return hass.states.get(entity_id)

    # 1. Total Active Power
    state = get_state_by_key("total_active_power")
    assert state
    assert float(state.state) == 11000.0
    assert state.attributes["unit_of_measurement"] == UnitOfPower.WATT
    assert state.attributes["device_class"] == SensorDeviceClass.POWER

    # 2. Housing Temperature
    state = get_state_by_key("housing_temperature")
    assert state
    assert float(state.state) == 35.0
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    # 3. Charging Status (mapped)
    state = get_state_by_key("status")
    assert state
    assert state.state == "Charging"  # STATUS_MAP[3]

    # 4. Info Sensor (Rated Current)
    state = get_state_by_key("rated_current")
    assert state
    assert float(state.state) == 32.0

    # 5. Charging Current (measured)
    state = get_state_by_key("charging_current")
    assert state
    assert float(state.state) == 16.0

    # 6. Set Current (from control data - separate from the number entity)
    state = get_state_by_key("current_set")
    assert state
    assert float(state.state) == 16.0
