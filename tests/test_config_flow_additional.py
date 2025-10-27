"""Additional tests for NRGkick config flow edge cases."""

from __future__ import annotations

from ipaddress import ip_address
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from custom_components.nrgkick.api import NRGkickApiClientAuthenticationError
from custom_components.nrgkick.const import CONF_SCAN_INTERVAL

from . import create_mock_config_entry

# Reauth Flow Additional Tests


@pytest.mark.requires_integration
async def test_reauth_flow_invalid_auth(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test reauth flow with invalid authentication."""
    entry = create_mock_config_entry(
        domain="nrgkick",
        title="NRGkick Test",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "old_user",
            CONF_PASSWORD: "old_pass",
        },
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        "nrgkick",
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    mock_nrgkick_api.test_connection.side_effect = NRGkickApiClientAuthenticationError

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "wrong_user",
                CONF_PASSWORD: "wrong_pass",
            },
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}


@pytest.mark.requires_integration
async def test_reauth_flow_unknown_exception(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test reauth flow with unexpected exception."""
    entry = create_mock_config_entry(
        domain="nrgkick",
        title="NRGkick Test",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        "nrgkick",
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    mock_nrgkick_api.test_connection.side_effect = Exception("Unexpected error")

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "new_user",
                CONF_PASSWORD: "new_pass",
            },
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


# Options Flow Additional Tests


@pytest.mark.requires_integration
async def test_options_flow_unknown_exception(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow with an unknown exception."""
    entry = create_mock_config_entry(
        domain="nrgkick",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    with patch(
        "custom_components.nrgkick.config_flow.validate_input",
        side_effect=Exception("Unexpected error"),
    ):
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


@pytest.mark.requires_integration
async def test_options_flow_scan_interval_only(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow changing only scan_interval without host changes."""
    entry = create_mock_config_entry(
        domain="nrgkick",
        title="NRGkick Test",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
        options={CONF_SCAN_INTERVAL: 30},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    # Set up the entry to register the update listener
    with patch(
        "custom_components.nrgkick.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ), patch("homeassistant.config_entries.ConfigEntries.async_reload"):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)

    with patch(
        "custom_components.nrgkick.config_flow.validate_input",
        return_value={"title": "NRGkick Test", "serial": "TEST123456"},
    ), patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload:
        # Change only scan_interval, keeping host/credentials the same
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.100",  # Same
                CONF_USERNAME: "test_user",  # Same
                CONF_PASSWORD: "test_pass",  # Same
                CONF_SCAN_INTERVAL: 120,  # Changed
            },
        )
        await hass.async_block_till_done()

        assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result2["data"] == {CONF_SCAN_INTERVAL: 120}

        # Verify reload was triggered
        assert len(mock_reload.mock_calls) >= 1


@pytest.mark.requires_integration
async def test_options_flow_with_empty_credentials(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow when removing credentials (setting them to empty)."""
    entry = create_mock_config_entry(
        domain="nrgkick",
        title="NRGkick Test",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "old_user",
            CONF_PASSWORD: "old_pass",
        },
        options={CONF_SCAN_INTERVAL: 30},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    # Set up the entry to register the update listener
    with patch(
        "custom_components.nrgkick.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ), patch("homeassistant.config_entries.ConfigEntries.async_reload"):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)

    with patch(
        "custom_components.nrgkick.config_flow.validate_input",
        return_value={"title": "NRGkick Test", "serial": "TEST123456"},
    ), patch("homeassistant.config_entries.ConfigEntries.async_reload"):
        # Submit with empty credentials (device doesn't require auth)
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.100",
                CONF_USERNAME: "",  # Empty
                CONF_PASSWORD: "",  # Empty
                CONF_SCAN_INTERVAL: 30,
            },
        )
        await hass.async_block_till_done()

        assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

        # Verify credentials were updated (empty strings become None)
        updated_entry = hass.config_entries.async_get_entry(entry.entry_id)
        assert updated_entry is not None
        # Empty strings are stored as None or empty string depending on implementation
        assert updated_entry.data[CONF_USERNAME] in [None, ""]
        assert updated_entry.data[CONF_PASSWORD] in [None, ""]


# Zeroconf Additional Tests


@pytest.mark.requires_integration
async def test_zeroconf_discovery_invalid_auth(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test zeroconf discovery with authentication error."""
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.100"),
        ip_addresses=[ip_address("192.168.1.100")],
        hostname="nrgkick.local.",
        name="NRGkick Test._nrgkick._tcp.local.",
        port=80,
        properties={
            "serial_number": "TEST123456",
            "device_name": "NRGkick Test",
            "json_api_enabled": "1",
        },
        type="_nrgkick._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        "nrgkick",
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    mock_nrgkick_api.test_connection.side_effect = NRGkickApiClientAuthenticationError

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "wrong_user",
                CONF_PASSWORD: "wrong_pass",
            },
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}


@pytest.mark.requires_integration
async def test_zeroconf_discovery_unknown_exception(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test zeroconf discovery with unexpected exception."""
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.100"),
        ip_addresses=[ip_address("192.168.1.100")],
        hostname="nrgkick.local.",
        name="NRGkick Test._nrgkick._tcp.local.",
        port=80,
        properties={
            "serial_number": "TEST123456",
            "device_name": "NRGkick Test",
            "json_api_enabled": "1",
        },
        type="_nrgkick._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        "nrgkick",
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    mock_nrgkick_api.test_connection.side_effect = Exception("Unexpected error")

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


@pytest.mark.requires_integration
async def test_zeroconf_fallback_to_default_name(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test zeroconf when device_name and model_type are missing."""
    discovery_info = ZeroconfServiceInfo(
        ip_address=ip_address("192.168.1.100"),
        ip_addresses=[ip_address("192.168.1.100")],
        hostname="nrgkick.local.",
        name="Unknown Device._nrgkick._tcp.local.",
        port=80,
        properties={
            "serial_number": "TEST123456",
            "json_api_enabled": "1",
            # No device_name
            # No model_type
        },
        type="_nrgkick._tcp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        "nrgkick",
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    # Should fallback to "NRGkick"
    assert result["description_placeholders"] == {"name": "NRGkick"}
