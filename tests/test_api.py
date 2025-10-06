"""Tests for the NRGkick API client."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientError, ClientResponseError

from custom_components.nrgkick.api import NRGkickAPI


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"test": "data"})
    response.raise_for_status = AsyncMock()
    session.get.return_value.__aenter__.return_value = response
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
    assert call_args[1]["params"] == {"current": 16.0}


async def test_set_charge_pause(mock_session):
    """Test set_charge_pause API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    # Test pause
    await api.set_charge_pause(True)
    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"pause": "1"}

    # Test resume
    await api.set_charge_pause(False)
    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"pause": "0"}


async def test_set_energy_limit(mock_session):
    """Test set_energy_limit API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.set_energy_limit(5000)

    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"energy": 5000}


async def test_set_phase_count(mock_session):
    """Test set_phase_count API call."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)

    await api.set_phase_count(3)

    call_args = mock_session.get.call_args
    assert call_args[1]["params"] == {"phases": 3}


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


async def test_test_connection_success(mock_session):
    """Test successful connection test."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "general": {"device_name": "Test"}
    }

    result = await api.test_connection()

    assert result is True


async def test_test_connection_failure(mock_session):
    """Test failed connection test."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.raise_for_status.side_effect = (
        ClientError()
    )

    result = await api.test_connection()

    assert result is False


async def test_api_timeout(mock_session):
    """Test API timeout handling."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.side_effect = TimeoutError()

    with pytest.raises(TimeoutError):
        await api.get_info()


async def test_api_client_error(mock_session):
    """Test API client error handling."""
    api = NRGkickAPI(host="192.168.1.100", session=mock_session)
    mock_session.get.return_value.__aenter__.return_value.raise_for_status.side_effect = ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=500,
        message="Internal Server Error",
    )

    with pytest.raises(ClientResponseError):
        await api.get_info()
