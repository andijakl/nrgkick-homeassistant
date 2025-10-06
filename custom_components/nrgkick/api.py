"""NRGkick API client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

import aiohttp

_LOGGER = logging.getLogger(__name__)


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

        async with asyncio.timeout(10):
            async with session.get(
                url, auth=auth, params=request_params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if data is None:
                    return {}
                return data

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
        return await self._request("/control", {"current": current})

    async def set_charge_pause(self, pause: bool) -> dict[str, Any]:
        """Set charge pause state."""
        return await self._request("/control", {"pause": "1" if pause else "0"})

    async def set_energy_limit(self, limit: int) -> dict[str, Any]:
        """Set energy limit in Wh (0 = no limit)."""
        return await self._request("/control", {"energy": limit})

    async def set_phase_count(self, phases: int) -> dict[str, Any]:
        """Set phase count (1-3)."""
        if phases not in [1, 2, 3]:
            raise ValueError("Phase count must be 1, 2, or 3")
        return await self._request("/control", {"phases": phases})

    async def test_connection(self) -> bool:
        """Test if we can connect to the device."""
        try:
            await self.get_info(["general"])
            return True
        except Exception as err:
            _LOGGER.error("Failed to connect to NRGkick: %s", err)
            return False
