"""NRGkick API client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

import aiohttp
from aiohttp import ClientError
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Retry configuration for transient errors
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.5  # seconds
RETRY_STATUSES = {500, 502, 503, 504}  # Transient HTTP errors to retry


class NRGkickApiClientError(HomeAssistantError):
    """Base exception for NRGkick API client errors."""

    translation_domain = DOMAIN
    translation_key = "unknown_error"


class NRGkickApiClientCommunicationError(NRGkickApiClientError):
    """Exception for NRGkick API client communication errors."""

    translation_domain = DOMAIN
    translation_key = "communication_error"


class NRGkickApiClientAuthenticationError(NRGkickApiClientError):
    """Exception for NRGkick API client authentication errors."""

    translation_domain = DOMAIN
    translation_key = "authentication_error"


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

    def _handle_auth_error(self, response_status: int, url: str) -> None:
        """Handle authentication errors with detailed logging."""
        error_msg = (
            f"Authentication failed (HTTP {response_status}). "
            "Verify that BasicAuth is enabled in the NRGkick app "
            "(Extended → Local API → Authentication (JSON)) and that "
            "the username and password are correct (case-sensitive). "
            f"Attempted to access: {url}"
        )
        _LOGGER.warning(error_msg)
        raise NRGkickApiClientAuthenticationError(error_msg)

    def _handle_timeout_error(self, exc: asyncio.TimeoutError, url: str) -> None:
        """Handle timeout errors with detailed troubleshooting info."""
        error_msg = (
            f"Connection timeout after {MAX_RETRIES} attempts. "
            "Verify: (1) The NRGkick device is powered on and "
            "the LED is active, (2) The device is reachable on "
            f"the network (try: ping {self.host!r}), "
            "(3) Home Assistant and NRGkick are on the same "
            "network/VLAN, (4) No firewall is blocking HTTP "
            f"traffic on port 80. Target: {url}"
        )
        _LOGGER.error(error_msg)
        raise NRGkickApiClientCommunicationError(error_msg) from exc

    def _handle_http_error(self, exc: aiohttp.ClientResponseError, url: str) -> None:
        """Handle HTTP response errors with troubleshooting info."""
        error_msg = (
            f"Device returned HTTP error {exc.status} ({exc.message}). "
            "This usually indicates: (1) The requested action is not "
            "allowed in the current device state, (2) The API endpoint "
            "doesn't exist (check firmware version is up to date), or "
            "(3) The device rejected the request parameters. "
            f"URL: {url}"
        )
        _LOGGER.error(error_msg)
        raise NRGkickApiClientCommunicationError(error_msg) from exc

    def _handle_connection_error(
        self,
        exc: aiohttp.ClientConnectorError | aiohttp.ClientOSError,
        url: str,
    ) -> None:
        """Handle connection errors with troubleshooting info."""
        error_msg = (
            f"Network connection failed after {MAX_RETRIES} attempts: "
            f"{exc}. Check: (1) The IP address {self.host!r} is correct, "
            "(2) The device is on the same network as Home Assistant, "
            "(3) There are no network issues (try ping or traceroute), "
            f"(4) The device is not blocking connections. Target: {url}"
        )
        _LOGGER.error(error_msg)
        raise NRGkickApiClientCommunicationError(error_msg) from exc

    def _handle_generic_error(self, exc: ClientError, url: str) -> None:
        """Handle generic client errors with troubleshooting info."""
        error_msg = (
            f"Connection failed after {MAX_RETRIES} attempts: {exc}. "
            "This may indicate a network problem or device issue. "
            "Try: (1) Restarting the NRGkick device, "
            "(2) Checking network connectivity, "
            "(3) Verifying the device firmware is up to date. "
            f"Target: {url}"
        )
        _LOGGER.error(error_msg)
        raise NRGkickApiClientCommunicationError(error_msg) from exc

    async def _make_request_attempt(
        self,
        *,
        session: aiohttp.ClientSession,
        url: str,
        auth: aiohttp.BasicAuth | None,
        params: dict[str, Any],
        attempt: int,
    ) -> dict[str, Any] | None:
        """Make a single request attempt, handling transient errors.

        Returns:
            Response data if successful, None if should retry
        """
        async with asyncio.timeout(10):
            async with session.get(url, auth=auth, params=params) as response:
                # Check authentication (don't retry)
                if response.status in (401, 403):
                    self._handle_auth_error(response.status, url)

                # Retry on transient HTTP errors
                if response.status in RETRY_STATUSES and attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF_BASE**attempt
                    _LOGGER.warning(
                        "Transient HTTP error %d from %s, "
                        "retrying in %.1f seconds (attempt %d/%d)",
                        response.status,
                        url,
                        wait_time,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    await asyncio.sleep(wait_time)
                    return None  # Signal retry needed

                # Read JSON response (even on errors)
                try:
                    data = await response.json()
                except Exception:  # pylint: disable=broad-exception-caught
                    response.raise_for_status()
                    return {}

                # Check HTTP status after reading JSON
                if response.status >= 400:
                    if "Response" not in data:
                        response.raise_for_status()

                return data if data is not None else {}

    async def _handle_retry_exception(
        self,
        exc: Exception,
        url: str,
        attempt: int,
    ) -> bool:
        """Handle exceptions during retry attempts.

        Returns:
            True if should retry, False if should raise
        """
        if isinstance(exc, asyncio.TimeoutError):
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF_BASE**attempt
                _LOGGER.warning(
                    "Connection timeout to %s, retrying in %.1f "
                    "seconds (attempt %d/%d)",
                    url,
                    wait_time,
                    attempt + 1,
                    MAX_RETRIES,
                )
                await asyncio.sleep(wait_time)
                return True
            self._handle_timeout_error(exc, url)

        elif isinstance(exc, aiohttp.ClientResponseError):
            # Don't retry 4xx client errors
            self._handle_http_error(exc, url)

        elif isinstance(exc, (aiohttp.ClientConnectorError, aiohttp.ClientOSError)):
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF_BASE**attempt
                _LOGGER.warning(
                    "Network error connecting to %s: %s. "
                    "Retrying in %.1f seconds (attempt %d/%d)",
                    url,
                    str(exc),
                    wait_time,
                    attempt + 1,
                    MAX_RETRIES,
                )
                await asyncio.sleep(wait_time)
                return True
            self._handle_connection_error(exc, url)

        elif isinstance(exc, ClientError):
            # Generic aiohttp errors - retry with backoff
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF_BASE**attempt
                _LOGGER.warning(
                    "Client error connecting to %s: %s. "
                    "Retrying in %.1f seconds (attempt %d/%d)",
                    url,
                    str(exc),
                    wait_time,
                    attempt + 1,
                    MAX_RETRIES,
                )
                await asyncio.sleep(wait_time)
                return True
            self._handle_generic_error(exc, url)

        return False

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the API with automatic retry."""
        if self._session is None:
            raise RuntimeError("Session not initialized")

        session = cast(aiohttp.ClientSession, self._session)
        url = f"{self._base_url}{endpoint}"
        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        request_params = params if params is not None else {}

        # Retry loop for transient errors
        last_exception: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                result = await self._make_request_attempt(
                    session=session,
                    url=url,
                    auth=auth,
                    params=request_params,
                    attempt=attempt,
                )
                if result is None:
                    # Transient error, retry requested
                    continue

                # Success - log if this was a retry
                if attempt > 0:
                    _LOGGER.info(
                        "Successfully connected to NRGkick "
                        "after %d retry attempt(s)",
                        attempt,
                    )
                return result

            except Exception as exc:  # pylint: disable=broad-exception-caught
                last_exception = exc
                should_retry = await self._handle_retry_exception(exc, url, attempt)
                if should_retry:
                    continue
                # Exception handler raised its own exception, won't reach here
                raise

        # Should never reach here, but just in case
        if last_exception:
            raise NRGkickApiClientCommunicationError(
                f"Failed after {MAX_RETRIES} attempts. " f"Last error: {last_exception}"
            ) from last_exception
        return {}

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
