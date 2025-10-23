"""Tests for the NRGkick integration initialization."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from custom_components.nrgkick import async_setup_entry
from custom_components.nrgkick.api import (
    NRGkickApiClientAuthenticationError,
    NRGkickApiClientCommunicationError,
)
from custom_components.nrgkick.const import DOMAIN

from . import async_setup_entry_with_return, create_mock_config_entry


@pytest.mark.requires_integration
async def test_setup_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test successful setup of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        # Use the config_entries.async_setup to properly set entry state
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_setup_entry_failed_connection(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test setup entry with failed connection."""
    mock_config_entry.add_to_hass(hass)

    mock_nrgkick_api.get_info.side_effect = Exception("Connection failed")

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"), pytest.raises(
        Exception
    ):
        await async_setup_entry(hass, mock_config_entry)


@pytest.mark.requires_integration
async def test_unload_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test successful unload of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        # Use proper setup to set entry state
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Use the config_entries.async_unload for proper state management
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.requires_integration
async def test_reload_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test reload of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        # Use proper setup to set entry state
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Test that reload calls the config_entries.async_reload
    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
        await hass.async_block_till_done()


@pytest.mark.requires_integration
async def test_coordinator_update_success(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_nrgkick_api,
    mock_info_data,
    mock_control_data,
    mock_values_data,
) -> None:
    """Test successful coordinator update."""
    mock_config_entry.add_to_hass(hass)

    mock_nrgkick_api.get_info.return_value = mock_info_data
    mock_nrgkick_api.get_control.return_value = mock_control_data
    mock_nrgkick_api.get_values.return_value = mock_values_data

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        # Use proper setup to set entry state
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        assert coordinator.data == {
            "info": mock_info_data,
            "control": mock_control_data,
            "values": mock_values_data,
        }


async def test_coordinator_update_failed(
    hass: HomeAssistant, mock_nrgkick_api, caplog
) -> None:
    """Test coordinator update failed."""
    entry = create_mock_config_entry(data={CONF_HOST: "192.168.1.100"})
    entry.add_to_hass(hass)
    mock_nrgkick_api.get_values.side_effect = NRGkickApiClientCommunicationError

    with patch(
        "custom_components.nrgkick.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        await async_setup_entry_with_return(hass, entry)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_coordinator_auth_failed(
    hass: HomeAssistant, mock_nrgkick_api, caplog
) -> None:
    """Test coordinator auth failed."""
    entry = create_mock_config_entry(data={CONF_HOST: "192.168.1.100"})
    entry.add_to_hass(hass)
    mock_nrgkick_api.get_values.side_effect = NRGkickApiClientAuthenticationError

    with patch(
        "custom_components.nrgkick.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        await async_setup_entry_with_return(hass, entry)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_ERROR
