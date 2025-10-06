"""Tests for the NRGkick integration initialization."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientResponseError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.nrgkick import (
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.nrgkick.const import DOMAIN


async def test_setup_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test successful setup of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]
    assert len(hass.config_entries.async_forward_entry_setups.mock_calls) == 1


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


async def test_unload_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test successful unload of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

    assert await async_unload_entry(hass, mock_config_entry)
    await hass.async_block_till_done()

    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


async def test_reload_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test reload of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"):
        await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as mock_reload:
        await async_reload_entry(hass, mock_config_entry)
        assert len(mock_reload.mock_calls) == 1


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
        await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        assert coordinator.data == {
            "info": mock_info_data,
            "control": mock_control_data,
            "values": mock_values_data,
        }


async def test_coordinator_update_failed(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test coordinator update failure."""
    mock_config_entry.add_to_hass(hass)

    mock_nrgkick_api.get_info.side_effect = Exception("Update failed")

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"), pytest.raises(
        Exception
    ):
        await async_setup_entry(hass, mock_config_entry)


async def test_coordinator_auth_failed(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_nrgkick_api
) -> None:
    """Test coordinator handles authentication failure."""
    mock_config_entry.add_to_hass(hass)

    # Create a mock 401 response error
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_error = ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=401,
        message="Unauthorized",
    )

    mock_nrgkick_api.get_info.side_effect = mock_error

    with patch(
        "custom_components.nrgkick.NRGkickAPI", return_value=mock_nrgkick_api
    ), patch("custom_components.nrgkick.async_get_clientsession"), pytest.raises(
        ConfigEntryAuthFailed
    ):
        await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        # Manually trigger update to test auth failure
        await coordinator.async_refresh()
