"""Tests for the NRGkick config flow."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nrgkick.const import CONF_SCAN_INTERVAL, DOMAIN


@pytest.mark.requires_integration
async def test_form(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ), patch(
        "custom_components.nrgkick.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_USERNAME: "test_user",
                CONF_PASSWORD: "test_pass",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "NRGkick Test"
    assert result2["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
    }
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.requires_integration
async def test_form_without_credentials(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test we can setup without credentials."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ), patch(
        "custom_components.nrgkick.async_setup_entry",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "NRGkick Test"
    assert result2["data"] == {CONF_HOST: "192.168.1.100"}


@pytest.mark.requires_integration
async def test_form_cannot_connect(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_nrgkick_api.test_connection.return_value = False

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


@pytest.mark.requires_integration
async def test_form_unknown_exception(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test we handle unknown exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_nrgkick_api.test_connection.side_effect = Exception("Unexpected error")

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


@pytest.mark.requires_integration
async def test_form_already_configured(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test we handle already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


@pytest.mark.requires_integration
async def test_reauth_flow(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test reauth flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
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
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
            "unique_id": entry.unique_id,
        },
        data=entry.data,
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

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

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"
    assert entry.data[CONF_USERNAME] == "new_user"
    assert entry.data[CONF_PASSWORD] == "new_pass"


@pytest.mark.requires_integration
async def test_reauth_flow_cannot_connect(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test reauth flow with connection error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    mock_nrgkick_api.test_connection.return_value = False

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

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


@pytest.mark.requires_integration
async def test_options_flow(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.200",
                CONF_USERNAME: "new_user",
                CONF_PASSWORD: "new_pass",
            },
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_HOST] == "192.168.1.200"
    assert entry.data[CONF_USERNAME] == "new_user"
    assert entry.data[CONF_PASSWORD] == "new_pass"


@pytest.mark.requires_integration
async def test_options_flow_cannot_connect(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow with connection error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    mock_nrgkick_api.test_connection.return_value = False

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.200"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


@pytest.mark.requires_integration
async def test_options_flow_with_scan_interval(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow with scan interval configuration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_USERNAME: "test_user",
                CONF_PASSWORD: "test_pass",
                CONF_SCAN_INTERVAL: 60,
            },
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SCAN_INTERVAL] == 60


@pytest.mark.requires_integration
async def test_options_flow_invalid_scan_interval(
    hass: HomeAssistant, mock_nrgkick_api
) -> None:
    """Test options flow with invalid scan interval."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NRGkick Test",
        data={CONF_HOST: "192.168.1.100"},
        entry_id="test_entry",
        unique_id="TEST123456",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 5,  # Too low
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_SCAN_INTERVAL: "invalid_scan_interval"}

    with patch(
        "custom_components.nrgkick.config_flow.NRGkickAPI",
        return_value=mock_nrgkick_api,
    ):
        result3 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 500,  # Too high
            },
        )

    assert result3["type"] == FlowResultType.FORM
    assert result3["errors"] == {CONF_SCAN_INTERVAL: "invalid_scan_interval"}
