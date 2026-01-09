"""imports for device.py."""

import re


class Device:
    """Device Object that setup Uhoo sensors."""

    SENSOR_FIELDS = [
        "virusIndex",
        "moldIndex",
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
    virus_index: float
    mold_index: float
    temperature: float
    humidity: float
    pm25: float
    tvoc: float
    co2: float
    co: float
    air_pressure: float
    ozone: float
    no2: float

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
        self.user_settings: dict[str, str] = {}

        # Sensor averages (initialized to 0.0)
        for field in self.SENSOR_FIELDS:
            setattr(self, self._to_attr_name(field), 0.0)
        self.timestamp: int = -1

        self.update_device(device)

    def _to_attr_name(self, key: str) -> str:
        """Convert JSON-style keys to Python attributes (camelCase → snake_case)."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

    @property
    def as_dict(self) -> dict[str, float]:
        """Return sensor data as dictionary."""
        return {
            "co": self.co,
            "co2": self.co2,
            "pm25": self.pm25,
            "humidity": self.humidity,
            "temperature": self.temperature,
            "air_pressure": self.air_pressure,
            "tvoc": self.tvoc,
            "no2": self.no2,
            "ozone": self.ozone,
            "virus_index": self.virus_index,
            "mold_index": self.mold_index,
        }

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
        if not data_points:
            return  # No data to process

        # Compute averages
        n = len(data_points)
        sums = dict.fromkeys(self.SENSOR_FIELDS, 0.0)
        for entry in data_points:
            for field in self.SENSOR_FIELDS:
                value = entry.get(field)
                if isinstance(value, (int, float)):
                    sums[field] += value

        # Assign averages to class attributes
        for field in self.SENSOR_FIELDS:
            avg = sums[field] / n
            setattr(self, self._to_attr_name(field), round(avg, 1))

        # Optionally use the latest timestamp
        self.timestamp = data_points[-1].get("timestamp", -1)
        self.user_settings = user_settings
