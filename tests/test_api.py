"""Tests for the NRGkick API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock

import aiohttp
import pytest

from custom_components.nrgkick.api import (
    NRGkickAPI,
    NRGkickApiClientAuthenticationError,
    NRGkickApiClientCommunicationError,
)


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"test": "data"})
    response.raise_for_status = MagicMock()  # Not async, just a regular method

    # Create a proper async context manager mock
    mock_get = MagicMock()
    mock_get.__aenter__ = AsyncMock(return_value=response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=mock_get)

    return session


async def test_api_init():
    """Test API initialization."""
    api = NRGkickAPI(
        host="192.168.1.100",
        username="test_user",
        password="test_pass",
        session=AsyncMock(),
    )

    assert api.host == "192.168.1.100"
    assert api.username == "test_user"
    assert api.password == "test_pass"
    assert api._base_url == "http://192.168.1.100"


async def test_get_info(mock_session):
    """Test get_info API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "general": {"device_name": "Test"}
    }

    result = await api.get_info()

    assert result == {"general": {"device_name": "Test"}}
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args
    assert call_args[0][0] == "http://192.168.1.100/info"


async def test_get_info_with_sections(mock_session):
    """Test get_info with specific sections."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.get_info(["general", "network"])

    call_args = mock_session.get.call_args
    params = call_args[1]["params"]
    assert params == {"general": "1", "network": "1"}


async def test_get_control(mock_session):
    """Test get_control API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "charging_current": 16.0
    }

    result = await api.get_control()

    assert result == {"charging_current": 16.0}
    call_args = mock_session.get.call_args
    assert call_args[0][0] == "http://192.168.1.100/control"


async def test_get_values(mock_session):
    """Test get_values API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "powerflow": {"power": {"total": 11000}}
    }

    result = await api.get_values()

    assert result == {"powerflow": {"power": {"total": 11000}}}
    call_args = mock_session.get.call_args
    assert call_args[0][0] == "http://192.168.1.100/values"


async def test_get_values_with_sections(mock_session):
    """Test get_values with specific sections."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.get_values(["powerflow", "energy"])

    call_args = mock_session.get.call_args
    params = call_args[1]["params"]
    assert params == {"powerflow": "1", "energy": "1"}


async def test_set_current(mock_session):
    """Test set_current API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.set_current(16.0)

    call_args = mock_session.get.call_args
    assert call_args[0][0] == "http://192.168.1.100/control"
    assert call_args[1]["params"] == {"current_set": 16.0}


async def test_set_charge_pause(mock_session):
    """Test set_charge_pause API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    # Test pause
    await api.set_charge_pause(True)
    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"charge_pause": "1"}

    # Test resume
    await api.set_charge_pause(False)
    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"charge_pause": "0"}


async def test_set_energy_limit(mock_session):
    """Test set_energy_limit API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.set_energy_limit(5000)

    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"energy_limit": 5000}


async def test_set_phase_count(mock_session):
    """Test set_phase_count API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.set_phase_count(3)

    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"phase_count": 3}


async def test_set_phase_count_invalid():
    """Test set_phase_count with invalid value."""
    api = NRGkickAPI(host="192.168.1.100", session=AsyncMock())

    with pytest.raises(ValueError, match="Phase count must be 1, 2, or 3"):
        await api.set_phase_count(4)


async def test_api_with_auth(mock_session):
    """Test API calls with authentication."""
    api = NRGkickAPI(
        host="192.168.1.100",
        username="test_user",
        password="test_pass",
        session=mock_session,
    )

    await api.get_info()

    call_args = mock_session.get.call_args
    auth = call_args[1]["auth"]
    assert auth is not None
    assert auth.login == "test_user"
    assert auth.password == "test_pass"


async def test_test_connection_success(mock_session) -> None:
    """Test connection test success."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)
    assert await api.test_connection()


async def test_test_connection_failure(mock_session) -> None:
    """Test connection test failure."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)
    mock_session.get.side_effect = aiohttp.ClientError

    with pytest.raises(NRGkickApiClientCommunicationError):
        await api.test_connection()


async def test_api_timeout(mock_session) -> None:
    """Test API timeout."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)
    mock_session.get.side_effect = asyncio.TimeoutError

    with pytest.raises(NRGkickApiClientCommunicationError):
        await api.get_info()


async def test_api_client_error(mock_session) -> None:
    """Test API client error."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)
    mock_session.get.side_effect = aiohttp.ClientError

    with pytest.raises(NRGkickApiClientCommunicationError):
        await api.get_info()


async def test_api_auth_error(mock_session) -> None:
    """Test API authentication error."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.status = 401

    with pytest.raises(NRGkickApiClientAuthenticationError):
        await api.get_info()


async def test_api_http_error_with_json_response(mock_session) -> None:
    """Test API returns error status with JSON error message."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    # Mock a 405 error with JSON body containing error message
    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.status = 405
    response_mock.json = AsyncMock(
        return_value={"Response": "Charging pause is blocked by solar-charging"}
    )

    # Should return the JSON response even with 405 status
    result = await api.set_charge_pause(True)
    assert result == {"Response": "Charging pause is blocked by solar-charging"}


async def test_api_http_error_without_json_response(mock_session) -> None:
    """Test API returns error status without valid JSON (should raise)."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    # Mock a 500 error with invalid JSON
    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.status = 500
    response_mock.json = AsyncMock(side_effect=Exception("Invalid JSON"))
    response_mock.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(
            request_info=Mock(),
            history=(),
            status=500,
            message="Internal Server Error",
        )
    )

    # Should raise communication error since JSON parsing failed
    with pytest.raises(NRGkickApiClientCommunicationError):
        await api.get_control()


async def test_api_retry_on_timeout(mock_session) -> None:
    """Test API retries on timeout and eventually succeeds."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    # First 2 attempts timeout, 3rd succeeds
    attempt_count = 0

    def mock_get_with_retry(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count <= 2:
            raise asyncio.TimeoutError

        # Third attempt succeeds
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"general": {"serial_number": "123"}})
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=response)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        return mock_ctx

    mock_session.get = MagicMock(side_effect=mock_get_with_retry)

    # Should succeed after retries
    result = await api.get_info()
    assert result == {"general": {"serial_number": "123"}}
    assert attempt_count == 3  # Verify it tried 3 times


async def test_api_retry_on_transient_http_error(mock_session) -> None:
    """Test API retries on 503 Service Unavailable."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    attempt_count = 0

    def mock_get_with_503_then_success(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1

        response = AsyncMock()
        if attempt_count <= 2:
            # First 2 attempts return 503
            response.status = 503
        else:
            # Third attempt succeeds
            response.status = 200

        response.json = AsyncMock(return_value={"control": {"current_set": 16}})

        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=response)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        return mock_ctx

    mock_session.get = MagicMock(side_effect=mock_get_with_503_then_success)

    # Should succeed after retries
    result = await api.get_control()
    assert result == {"control": {"current_set": 16}}
    assert attempt_count == 3  # Verify it retried


async def test_api_retry_exhausted_on_timeout(mock_session) -> None:
    """Test API fails after exhausting all retries on timeout."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    # All attempts timeout
    mock_session.get.side_effect = asyncio.TimeoutError

    # Should raise after 3 attempts
    with pytest.raises(NRGkickApiClientCommunicationError) as exc_info:
        await api.get_info()

    assert exc_info.value.translation_key == "connection_timeout"


async def test_api_retry_on_connection_error(mock_session) -> None:
    """Test API retries on connection errors."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    attempt_count = 0

    def mock_get_with_connection_error(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count <= 2:
            # First 2 attempts have connection errors
            raise aiohttp.ClientConnectorError(
                connection_key=Mock(), os_error=OSError("Connection refused")
            )

        # Third attempt succeeds
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"values": {"status": {"charging": 1}}})
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=response)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        return mock_ctx

    mock_session.get = MagicMock(side_effect=mock_get_with_connection_error)

    # Should succeed after retries
    result = await api.get_values()
    assert result == {"values": {"status": {"charging": 1}}}
    assert attempt_count == 3


async def test_api_no_retry_on_auth_error(mock_session) -> None:
    """Test API does NOT retry on authentication errors."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    attempt_count = 0

    def mock_get_with_auth_error(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1

        response = AsyncMock()
        response.status = 401
        response.json = AsyncMock(return_value={})

        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=response)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        return mock_ctx

    mock_session.get = MagicMock(side_effect=mock_get_with_auth_error)

    # Should fail immediately without retries
    with pytest.raises(NRGkickApiClientAuthenticationError):
        await api.get_info()

    assert attempt_count == 1  # Should only try once


async def test_api_no_retry_on_client_error_4xx(mock_session) -> None:
    """Test API does NOT retry on 4xx client errors (except 401/403)."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    # Mock a 404 error
    response_mock = AsyncMock()
    response_mock.status = 404
    response_mock.json = AsyncMock(side_effect=Exception("Not found"))
    response_mock.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(
            request_info=Mock(),
            history=(),
            status=404,
            message="Not Found",
        )
    )

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=response_mock)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    mock_session.get.return_value = mock_ctx

    # Should fail immediately without retries
    with pytest.raises(NRGkickApiClientCommunicationError):
        await api.get_info()


async def test_api_retry_backoff_timing(mock_session) -> None:
    """Test that retry backoff timing works as expected."""
    api = NRGkickAPI("192.168.1.100", session=mock_session)

    attempt_count = 0
    attempt_times = []

    def mock_get_with_timing(*args, **kwargs):
        nonlocal attempt_count
        import time

        attempt_count += 1
        attempt_times.append(time.time())

        if attempt_count <= 2:
            raise asyncio.TimeoutError

        # Third attempt succeeds
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"test": "success"})
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=response)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        return mock_ctx

    mock_session.get = MagicMock(side_effect=mock_get_with_timing)

    # Should succeed after retries
    result = await api.get_info()
    assert result == {"test": "success"}
    assert attempt_count == 3

    # Check backoff timing (approximately)
    # First retry should wait ~1.5s (1.5^0), second ~1.5s (1.5^1)
    if len(attempt_times) >= 2:
        first_gap = attempt_times[1] - attempt_times[0]
        assert 1.0 < first_gap < 3.0  # Allow some variance

    if len(attempt_times) >= 3:
        second_gap = attempt_times[2] - attempt_times[1]
        assert 1.0 < second_gap < 3.0  # Allow some variance
