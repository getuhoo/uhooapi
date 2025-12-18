import pytest
import asyncio
from unittest.mock import AsyncMock
from aiohttp import ClientSession


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_websession():
    """Mock aiohttp ClientSession."""
    session = AsyncMock(spec=ClientSession)
    session.request = AsyncMock()
    return session


@pytest.fixture
def sample_device_data():
    """Sample device data from API."""
    return {
        "deviceName": "Living Room",
        "macAddress": "AA:BB:CC:DD:EE:FF",
        "serialNumber": "UHOO12345",
        "floorNumber": 1,
        "roomName": "Living Room",
        "timezone": "America/New_York",
        "utcOffset": "-05:00",
        "ssid": "HomeWiFi",
    }


@pytest.fixture
def sample_sensor_data():
    """Sample sensor data from API."""
    return {
        "data": [
            {
                "virusIndex": 2.5,
                "moldIndex": 1.8,
                "temperature": 22.5,
                "humidity": 45.0,
                "pm25": 12.3,
                "tvoc": 150.0,
                "co2": 800,
                "co": 0.5,
                "airPressure": 1013.25,
                "ozone": 0.02,
                "no2": 0.01,
                "pm1": 5.6,
                "pm4": 8.9,
                "pm10": 15.2,
                "ch2o": 0.03,
                "light": 300,
                "sound": 40,
                "h2s": 0.001,
                "no": 0.005,
                "so2": 0.002,
                "nh3": 0.008,
                "oxygen": 20.9,
                "timestamp": 1704067200,
            },
            {
                "virusIndex": 2.6,
                "moldIndex": 1.9,
                "temperature": 22.6,
                "humidity": 45.5,
                "pm25": 12.5,
                "tvoc": 155.0,
                "co2": 810,
                "co": 0.6,
                "airPressure": 1013.30,
                "ozone": 0.021,
                "no2": 0.011,
                "pm1": 5.7,
                "pm4": 9.0,
                "pm10": 15.5,
                "ch2o": 0.031,
                "light": 310,
                "sound": 42,
                "h2s": 0.0011,
                "no": 0.0051,
                "so2": 0.0021,
                "nh3": 0.0081,
                "oxygen": 20.91,
                "timestamp": 1704067260,
            },
        ]
    }


@pytest.fixture
def sample_token_response():
    """Sample token response from API."""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600,
    }


@pytest.fixture
def sample_device_list():
    """Sample device list from API."""
    return [
        {
            "deviceName": "Living Room",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "serialNumber": "UHOO12345",
            "floorNumber": 1,
            "roomName": "Living Room",
            "timezone": "America/New_York",
            "utcOffset": "-05:00",
            "ssid": "HomeWiFi",
        },
        {
            "deviceName": "Bedroom",
            "macAddress": "FF:EE:DD:CC:BB:AA",
            "serialNumber": "UHOO67890",
            "floorNumber": 2,
            "roomName": "Master Bedroom",
            "timezone": "America/New_York",
            "utcOffset": "-05:00",
            "ssid": "HomeWiFi",
        },
    ]
