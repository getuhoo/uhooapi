"""imports for device.py."""

import re


class Device:
    """Device Object that setup Uhoo sensors."""

    SENSOR_FIELDS = [
        "virusIndex",
        "moldIndex",
        "influenzaIndex",
        "temperature",
        "humidity",
        "pm25",
        "tvoc",
        "co2",
        "co",
        "airPressure",
        "ozone",
        "no2",
        "pm1",
        "pm4",
        "pm10",
        "ch2o",
        "light",
        "sound",
        "h2s",
        "no",
        "so2",
        "nh3",
        "oxygen",
    ]

    # Add type hints for ALL sensor fields
    virus_index: float | None
    mold_index: float | None
    influenza_index: float | None
    temperature: float | None
    humidity: float | None
    pm25: float | None
    tvoc: float | None
    co2: float | None
    co: float | None
    air_pressure: float | None
    ozone: float | None
    no2: float | None

    def __init__(self, device: dict) -> None:
        """Initialize Device."""
        # Device info
        self.device_name: str = ""
        self.mac_address: str = ""
        self.serial_number: str = ""
        self.floor_number: int = 0
        self.room_name: str = ""
        self.timezone: str = ""
        self.utc_offset: str = ""
        self.ssid: str = ""
        self.user_settings: dict[str, str] = {"temp": "c"}  # default to celsius

        # Sensor values (initialized to None = unavailable)
        for field in self.SENSOR_FIELDS:
            setattr(self, self._to_attr_name(field), None)
        self.timestamp: int = -1

        self.update_device(device)

    def _to_attr_name(self, key: str) -> str:
        """Convert JSON-style keys to Python attributes (camelCase → snake_case)."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

    def update_device(self, device: dict) -> None:
        """Update method for device info."""
        self.device_name = device.get("deviceName", "")
        self.mac_address = device.get("macAddress", "")
        self.serial_number = device.get("serialNumber", "")
        self.floor_number = device.get("floorNumber", 0)
        self.room_name = device.get("roomName", "")
        self.timezone = device.get("timezone", "")
        self.utc_offset = device.get("utcOffset", "")
        self.ssid = device.get("ssid", "")

    def update_data(self, data_points: list, user_settings: dict[str, str]) -> None:
        """Update sensor data."""
        if len(data_points) == 0:
            for field in self.SENSOR_FIELDS:
                setattr(self, self._to_attr_name(field), None)  # unavailable
                self.timestamp = -1  # default timestamp
                self.user_settings = user_settings
            return

        # Compute averages (only over entries with valid values)
        sums: dict[str, float] = dict.fromkeys(self.SENSOR_FIELDS, 0.0)
        counts: dict[str, int] = dict.fromkeys(self.SENSOR_FIELDS, 0)
        for entry in data_points:
            for field in self.SENSOR_FIELDS:
                value = entry.get(field)
                if isinstance(value, (int, float)):
                    sums[field] += value
                    counts[field] += 1

        # Assign averages to class attributes (None if no valid data)
        for field in self.SENSOR_FIELDS:
            if counts[field] > 0:
                avg = sums[field] / counts[field]
                setattr(self, self._to_attr_name(field), round(avg, 1))
            else:
                setattr(self, self._to_attr_name(field), None)

        # Optionally use the latest timestamp
        self.timestamp = data_points[-1].get("timestamp", -1)
        self.user_settings = user_settings

    def __repr__(self) -> str:
        """Return a readable representation of the Device."""
        sensors = {
            self._to_attr_name(f): getattr(self, self._to_attr_name(f))
            for f in self.SENSOR_FIELDS
            if getattr(self, self._to_attr_name(f)) is not None
        }
        return (
            f"Device(name={self.device_name!r}, serial={self.serial_number!r}, "
            f"sensors={sensors}, timestamp={self.timestamp})"
        )
