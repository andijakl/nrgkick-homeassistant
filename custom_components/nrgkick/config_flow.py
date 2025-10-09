"""Config flow for NRGkick integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NRGkickAPI
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = NRGkickAPI(
        host=data[CONF_HOST],
        username=data.get(CONF_USERNAME),
        password=data.get(CONF_PASSWORD),
        session=session,
    )

    if not await api.test_connection():
        raise CannotConnect

    info = await api.get_info(["general"])
    return {
        "title": info.get("general", {}).get("device_name", "NRGkick"),
        "serial": info.get("general", {}).get("serial_number", "Unknown"),
    }


# pylint: disable=abstract-method  # is_matching is not required for HA config flows
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for NRGkick."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_host: str | None = None
        self._discovered_name: str | None = None

    # pylint: disable=unused-argument

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["serial"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Discovered NRGkick device: %s", discovery_info)

        # Extract device information from mDNS metadata
        serial = discovery_info.properties.get("serial_number")
        device_name = discovery_info.properties.get("device_name", "NRGkick")
        model_type = discovery_info.properties.get("model_type", "NRGkick")
        json_api_enabled = discovery_info.properties.get("json_api_enabled", "0")

        # Verify JSON API is enabled
        if json_api_enabled != "1":
            _LOGGER.debug("NRGkick device %s does not have JSON API enabled", serial)
            return self.async_abort(reason="json_api_disabled")

        if not serial:
            _LOGGER.debug("NRGkick device discovered without serial number")
            return self.async_abort(reason="no_serial_number")

        # Set unique ID to prevent duplicate entries
        await self.async_set_unique_id(serial)
        # Update the host if the device is already configured (IP might have changed)
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.host})

        # Store discovery info for the confirmation step
        self._discovered_host = discovery_info.host
        self._discovered_name = device_name or model_type
        self.context["title_placeholders"] = {
            "name": self._discovered_name or "NRGkick"
        }

        # Proceed to confirmation step
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Build the connection data
            data = {
                CONF_HOST: self._discovered_host,
                CONF_USERNAME: user_input.get(CONF_USERNAME),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD),
            }

            try:
                info = await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=data)

        # Show confirmation form with optional authentication
        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            description_placeholders={"name": self._discovered_name or "NRGkick"},
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauthentication confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entry_id = self.context.get("entry_id")
            if not entry_id:
                return self.async_abort(reason="reauth_failed")

            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry is None:
                return self.async_abort(reason="reauth_failed")

            data = {
                CONF_HOST: entry.data[CONF_HOST],
                CONF_USERNAME: user_input.get(CONF_USERNAME),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD),
            }

            try:
                await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during reauthentication")
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(entry, data=data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for NRGkick."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate scan interval
            scan_interval = user_input.get(
                CONF_SCAN_INTERVAL,
                self.config_entry.options.get(
                    CONF_SCAN_INTERVAL,
                    self.config_entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ),
            )

            if scan_interval < MIN_SCAN_INTERVAL or scan_interval > MAX_SCAN_INTERVAL:
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"

            if not errors:
                try:
                    # Validate connection settings if provided
                    connection_data = {
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_USERNAME: user_input.get(CONF_USERNAME),
                        CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                    }
                    await validate_input(self.hass, connection_data)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    # Update the config entry with both connection data and options
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=connection_data,
                        options={CONF_SCAN_INTERVAL: scan_interval},
                    )
                    return self.async_create_entry(title="", data={})

        # Get current values with defaults
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        # Show current settings as defaults
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=self.config_entry.data.get(CONF_HOST, ""),
                ): str,
                vol.Optional(
                    CONF_USERNAME,
                    default=self.config_entry.data.get(CONF_USERNAME, ""),
                ): str,
                vol.Optional(
                    CONF_PASSWORD,
                    default=self.config_entry.data.get(CONF_PASSWORD, ""),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
