"""NRGkick API client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

import aiohttp
from aiohttp import ClientError

_LOGGER = logging.getLogger(__name__)


class NRGkickApiClientError(Exception):
    """Base exception for NRGkick API client errors."""


class NRGkickApiClientCommunicationError(NRGkickApiClientError):
    """Exception for NRGkick API client communication errors."""


class NRGkickApiClientAuthenticationError(NRGkickApiClientError):
    """Exception for NRGkick API client authentication errors."""


class NRGkickAPI:
    """API client for NRGkick."""

    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.username = username
        self.password = password
        self._session = session
        self._base_url = f"http://{host}"

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the API."""
        if self._session is None:
            raise RuntimeError("Session not initialized")

        session = cast(aiohttp.ClientSession, self._session)
        url = f"{self._base_url}{endpoint}"
        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        request_params = params if params is not None else {}

        try:
            async with asyncio.timeout(10):
                async with session.get(
                    url, auth=auth, params=request_params
                ) as response:
                    if response.status in (401, 403):
                        raise NRGkickApiClientAuthenticationError(
                            "Authentication failed. Check username and password "
                            "in NRGkick app settings."
                        )

                    # Always read JSON response first (even on errors)
                    # Device returns error messages in JSON body
                    try:
                        data = await response.json()
                    except Exception:  # pylint: disable=broad-exception-caught
                        # If JSON parsing fails, fall back to raising HTTP error
                        response.raise_for_status()
                        return {}

                    # Check HTTP status after reading JSON
                    # This allows us to access error messages in the response
                    if response.status >= 400:
                        # If response has error message, it will be handled by caller
                        # Otherwise raise HTTP error
                        if "Response" not in data:
                            response.raise_for_status()

                    if data is None:
                        return {}
                    return data
        except asyncio.TimeoutError as exc:
            raise NRGkickApiClientCommunicationError(
                "Connection timeout. Check if device is powered on "
                "and network is reachable."
            ) from exc
        except aiohttp.ClientResponseError as exc:
            raise NRGkickApiClientCommunicationError(
                f"Device returned error {exc.status} ({exc.message}). "
                f"This may indicate the device is in a state that "
                f"prevents this action."
            ) from exc
        except ClientError as exc:
            raise NRGkickApiClientCommunicationError(
                f"Connection failed: {exc}. "
                f"Check device IP address and network connection."
            ) from exc

    async def get_info(self, sections: list[str] | None = None) -> dict[str, Any]:
        """Get device information."""
        params = {}
        if sections:
            for section in sections:
                params[section] = "1"
        return await self._request("/info", params)

    async def get_control(self) -> dict[str, Any]:
        """Get control information."""
        return await self._request("/control")

    async def get_values(self, sections: list[str] | None = None) -> dict[str, Any]:
        """Get current values."""
        params = {}
        if sections:
            for section in sections:
                params[section] = "1"
        return await self._request("/values", params)

    async def set_current(self, current: float) -> dict[str, Any]:
        """Set charging current."""
        return await self._request("/control", {"current_set": current})

    async def set_charge_pause(self, pause: bool) -> dict[str, Any]:
        """Set charge pause state."""
        return await self._request("/control", {"charge_pause": "1" if pause else "0"})

    async def set_energy_limit(self, limit: int) -> dict[str, Any]:
        """Set energy limit in Wh (0 = no limit)."""
        return await self._request("/control", {"energy_limit": limit})

    async def set_phase_count(self, phases: int) -> dict[str, Any]:
        """Set phase count (1-3)."""
        if phases not in [1, 2, 3]:
            raise ValueError("Phase count must be 1, 2, or 3")
        return await self._request("/control", {"phase_count": phases})

    async def test_connection(self) -> bool:
        """Test if we can connect to the device."""
        await self.get_info(["general"])
        return True
