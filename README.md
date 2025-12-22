# uhooapi - Python Client for uHoo API

[![PyPI version](https://img.shields.io/pypi/v/uhooapi.svg)](https://pypi.org/project/uhooapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/uhooapi.svg)](https://pypi.org/project/uhooapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A modern, asynchronous Python client for the uHoo air quality API. This library provides an intuitive, type-safe interface to access your uHoo device data, manage devices, and retrieve real-time air quality metrics with automatic token management and comprehensive error handling.

## ✨ Features

- **🚀 Async/Await Native**: Built on `aiohttp` for high-performance, non-blocking API calls
- **🔐 Automatic Token Management**: Handles authentication, token refresh, and retry logic automatically
- **📝 Full Type Annotations**: Complete type hints for better IDE support and reliability
- **🎯 Production Ready**: 100% test coverage with comprehensive unit and integration tests
- **🔄 Smart Error Handling**: Custom exceptions with automatic retry for 401/403 errors
- **📊 Complete Sensor Coverage**: Access to all uHoo metrics (temperature, humidity, CO₂, PM2.5, virus index, etc.)
- **⚡ Efficient Data Processing**: Automatic averaging and rounding of sensor readings

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install uhooapi
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/uhooapi.git
cd uhooapi

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify
pytest
```

## 🚀 Quick Start
```python
import asyncio
import aiohttp
from uhooapi import Client

async def main():
    # Create a session and client
    async with aiohttp.ClientSession() as session:
        client = Client(
            api_key="your_uhoo_api_key_here",  # Get from uHoo dashboard
            websession=session,
            debug=True  # Enable debug logging
        )

        # Authenticate and get token
        await client.login()

        # Discover and set up your devices
        await client.setup_devices()

        # Get all devices
        devices = client.get_devices()
        print(f"📱 Found {len(devices)} uHoo device(s)")

        # Get latest data for the first device
        if devices:
            first_device_serial = list(devices.keys())[0]
            await client.get_latest_data(first_device_serial)

            # Access the device data
            device = devices[first_device_serial]
            print(f"\n🏠 Device: {device.device_name}")
            print(f"📍 Location: {device.room_name}")
            print(f"🌡️ Temperature: {device.temperature}°C")
            print(f"💧 Humidity: {device.humidity}%")
            print(f"☁️ CO₂: {device.co2} ppm")
            print(f"💨 PM2.5: {device.pm25} µg/m³")
            print(f"🦠 Virus Risk Index: {device.virus_index}")

# Run the async function
asyncio.run(main())
```

## 📖 Usage Examples
### 🔄 Continuous Monitoring
```python
import asyncio
from datetime import datetime
from uhooapi import Client

async def monitor_air_quality(api_key: str, update_interval: int = 300):
    """Continuously monitor air quality and log changes."""
    async with aiohttp.ClientSession() as session:
        client = Client(api_key=api_key, websession=session)
        await client.login()
        await client.setup_devices()

        print("Starting air quality monitoring...")
        while True:
            for serial_number, device in client.get_devices().items():
                await client.get_latest_data(serial_number)

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                print(f"Device: {device.device_name} ({device.room_name})")
                print("-" * 40)
                print(f"Temperature: {device.temperature:5.1f}°C")
                print(f"Humidity:    {device.humidity:5.1f}%")
                print(f"CO₂:         {device.co2:5.0f} ppm")
                print(f"PM2.5:       {device.pm25:5.1f} µg/m³")
                print(f"Virus Index: {device.virus_index:5.1f}")

                # Add alerts for poor air quality
                if device.co2 > 1000:
                    print("⚠️  Warning: High CO₂ levels detected!")
                if device.pm25 > 35:
                    print("⚠️  Warning: Elevated PM2.5 levels!")

            await asyncio.sleep(update_interval)
```

### 🛡️ Robust Error Handling
```python
from uhooapi.errors import UnauthorizedError, ForbiddenError, RequestError

async def fetch_with_retry(client: Client, serial_number: str, max_retries: int = 3):
    """Fetch data with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            await client.get_latest_data(serial_number)
            return True

        except UnauthorizedError as e:
            print(f"❌ Authentication failed: {e}")
            # Re-authenticate and retry
            await client.login()
            continue

        except ForbiddenError as e:
            print(f"🔒 Permission denied: {e}")
            return False

        except RequestError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"🌐 Request failed (attempt {attempt + 1}/{max_retries}), "
                      f"retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"💥 Max retries exceeded: {e}")
                return False

    return False
```

### 📈 Multi-Device Data Aggregation
```python
async def get_environmental_summary(api_key: str):
    """Get summary statistics across all devices."""
    async with aiohttp.ClientSession() as session:
        client = Client(api_key=api_key, websession=session)
        await client.login()
        await client.setup_devices()

        devices = client.get_devices()

        # Fetch data for all devices concurrently
        tasks = [
            client.get_latest_data(serial)
            for serial in devices.keys()
        ]
        await asyncio.gather(*tasks)

        # Calculate averages
        temps = [d.temperature for d in devices.values()]
        humidities = [d.humidity for d in devices.values()]
        co2_levels = [d.co2 for d in devices.values()]

        print("\n📊 Environmental Summary")
        print("=" * 40)
        print(f"Total Devices: {len(devices)}")
        print(f"Avg Temperature: {sum(temps)/len(temps):.1f}°C")
        print(f"Avg Humidity: {sum(humidities)/len(humidities):.1f}%")
        print(f"Avg CO₂: {sum(co2_levels)/len(co2_levels):.0f} ppm")

        # Identify problem areas
        worst_co2 = max(devices.values(), key=lambda d: d.co2)
        if worst_co2.co2 > 800:
            print(f"\n⚠️  Highest CO₂ in: {worst_co2.room_name} ({worst_co2.co2} ppm)")
```
## 🏗️ Architecture

### Client Class (uhooapi.client.Client)
```python
Client(
    api_key: str,                    # Your uHoo API key
    websession: aiohttp.ClientSession,  # aiohttp session
    **kwargs                         # Optional: debug=True for debug logging
)
```

### Device Class (uhooapi.device.Device)
```python
device.device_name      # "Living Room"
device.serial_number    # "UHOO12345"
device.mac_address      # "AA:BB:CC:DD:EE:FF"
device.room_name        # "Living Room"
device.floor_number     # 1

device.temperature      # 22.5°C
device.humidity         # 45.0%
device.co2              # 800 ppm
device.pm25             # 12.3 µg/m³
device.virus_index      # 2.5
device.mold_index       # 1.8
device.tvoc             # 150.0 ppb
# ... and 15+ more sensors
```

## 🚨 Error Handling
The library defines custom exceptions for different error scenarios:

```python
from uhooapi.errors import (
    UhooError,          # Base exception
    RequestError,       # General API failures
    UnauthorizedError,  # 401 - Invalid/expired token
    ForbiddenError      # 403 - Insufficient permissions
)

try:
    await client.get_latest_data("UHOO12345")
except UnauthorizedError:
    # Automatic retry with fresh login is built-in
    print("Token expired, re-authenticating...")
except ForbiddenError as e:
    print(f"Access denied: {e.message}")
except RequestError as e:
    print(f"API request failed (status: {e.status}): {e}")
except KeyError:
    print("Device not found. Did you call setup_devices()?")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🧪 Testing
The project includes a comprehensive test suite:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/uhooapi --cov-report=html

# Run specific test categories
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # Integration tests

# Run tests in parallel
pytest -n auto
```

## 🔧 Building and Publishing
```bash
# Update version in pyproject.toml first!

# Build distribution packages
python -m build

# Check build quality
twine check dist/*

# Upload to TestPyPI (for testing)
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## 📁 Project Structure
```text
uhooapi/
├── src/uhooapi/               # Source code
│   ├── __init__.py           # Package exports
│   ├── client.py             # Main Client class
│   ├── api.py                # Low-level API wrapper
│   ├── device.py             # Device data model (22+ sensors)
│   ├── errors.py             # Custom exceptions
│   ├── const.py              # Constants and defaults
│   ├── endpoints.py          # API endpoint configurations
│   └── util.py               # Utility functions
├── tests/                    # Test suite
│   ├── unit/                # Unit tests (mocked)
│   │   ├── test_client.py   # Client tests
│   │   ├── test_api.py      # API tests
│   │   └── test_device.py   # Device model tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Test fixtures
├── pyproject.toml           # Package configuration
├── README.md                # This file
├── pre-commit-config.yaml   # Code quality hooks
└── .github/workflows/       # CI/CD pipelines (optional)
```

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. Fork the repository

2. Clone your fork: git clone https://github.com/yourusername/uhooapi.git

3. Create a branch: git checkout -b feature/amazing-feature

4. Make your changes and add tests

5. Run tests: pytest && pre-commit run --all-files

6. Commit: git commit -m 'Add amazing feature'

7. Push: git push origin feature/amazing-feature

8. Open a Pull Request
