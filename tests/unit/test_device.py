from uhooapi.device import Device

_USER_SETTINGS = {
    "temperature": "°C",
    "temp": "c",
    "humidity": "%",
    "pm25": "µg/m^3",
    "dust": "µg/m^3",
    "tvoc": "ppb",
    "voc": "ppb",
    "co2": "ppm",
    "co": "ppm",
    "airPressure": "mbar",
    "ozone": "ppb",
    "no2": "ppb",
}


class TestDeviceInitialization:
    """Test Device class initialization."""

    def test_device_init_empty(self):
        """Test device initialization with empty dict."""
        device = Device({})

        # Default values
        assert device.device_name == ""
        assert device.mac_address == ""
        assert device.serial_number == ""
        assert device.floor_number == 0
        assert device.room_name == ""
        assert device.timezone == ""
        assert device.utc_offset == ""
        assert device.ssid == ""

        # Sensor fields should be initialized to 0.0
        assert device.virus_index == 0.0
        assert device.mold_index == 0.0
        assert device.temperature == 0.0
        assert device.humidity == 0.0
        assert device.timestamp == -1

    def test_device_init_with_data(self):
        """Test device initialization with data."""
        device_data = {
            "deviceName": "Living Room",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "serialNumber": "UHOO12345",
            "floorNumber": 1,
            "roomName": "Living Room",
            "timezone": "America/New_York",
            "utcOffset": "-05:00",
            "ssid": "HomeWiFi",
        }

        device = Device(device_data)

        assert device.device_name == "Living Room"
        assert device.mac_address == "AA:BB:CC:DD:EE:FF"
        assert device.serial_number == "UHOO12345"
        assert device.floor_number == 1
        assert device.room_name == "Living Room"
        assert device.timezone == "America/New_York"
        assert device.utc_offset == "-05:00"
        assert device.ssid == "HomeWiFi"


class TestDeviceUpdate:
    """Test device update methods."""

    def test_update_device(self):
        """Test update_device method."""
        device = Device({})

        new_data = {
            "deviceName": "Updated Name",
            "macAddress": "FF:EE:DD:CC:BB:AA",
            "serialNumber": "UHOO99999",
            "floorNumber": 2,
            "roomName": "Bedroom",
            "timezone": "America/Los_Angeles",
            "utcOffset": "-08:00",
            "ssid": "UpdatedWiFi",
        }

        device.update_device(new_data)

        assert device.device_name == "Updated Name"
        assert device.mac_address == "FF:EE:DD:CC:BB:AA"
        assert device.serial_number == "UHOO99999"
        assert device.floor_number == 2
        assert device.room_name == "Bedroom"
        assert device.timezone == "America/Los_Angeles"
        assert device.utc_offset == "-08:00"
        assert device.ssid == "UpdatedWiFi"

    def test_update_device_partial(self):
        """Test update_device with partial data."""
        # Create a device with initial values
        device = Device({"deviceName": "Original", "serialNumber": "ORIG123"})

        # According to your actual code, update_device uses .get() with default values
        # So when we update with only deviceName, all other fields get set to their defaults
        device.update_device({"deviceName": "Updated"})

        # Based on your actual code behavior:
        assert device.device_name == "Updated"
        assert device.serial_number == ""  # .get("serialNumber", "") returns ""
        assert device.mac_address == ""  # .get("macAddress", "") returns ""
        assert device.floor_number == 0  # .get("floorNumber", 0) returns 0
        assert device.room_name == ""  # .get("roomName", "") returns ""
        assert device.timezone == ""  # .get("timezone", "") returns ""
        assert device.utc_offset == ""  # .get("utcOffset", "") returns ""
        assert device.ssid == ""  # .get("ssid", "") returns ""


class TestDeviceDataUpdate:
    """Test device data update methods."""

    def test_update_data_empty(self):
        """Test update_data with empty list."""
        device = Device({})

        # Store initial values
        initial_temp = device.temperature

        device.update_data([], _USER_SETTINGS)

        # Values should remain unchanged
        assert device.temperature == initial_temp

    def test_update_data_single_point(self):
        """Test update_data with single data point."""
        device = Device({})

        data_points = [
            {"temperature": 22.5, "humidity": 45.0, "co2": 800, "pm25": 12.3}
        ]

        device.update_data(data_points, _USER_SETTINGS)

        assert device.temperature == 22.5
        assert device.humidity == 45.0
        assert device.co2 == 800.0
        assert device.pm25 == 12.3

    def test_update_data_multiple_points(self):
        """Test update_data with multiple data points (averaging)."""
        device = Device({})

        data_points = [
            {"temperature": 20.0, "humidity": 40.0, "co2": 700},
            {"temperature": 22.0, "humidity": 45.0, "co2": 750},
            {"temperature": 24.0, "humidity": 50.0, "co2": 800},
        ]

        device.update_data(data_points, _USER_SETTINGS)

        # Averages: temp = (20+22+24)/3 = 22.0, humidity = (40+45+50)/3 = 45.0
        assert device.temperature == 22.0
        assert device.humidity == 45.0
        assert device.co2 == 750.0  # (700+750+800)/3 = 750

    def test_update_data_with_missing_values(self):
        """Test update_data with some missing values in data points."""
        device = Device({})

        data_points = [
            {"temperature": 20.0, "humidity": 40.0},
            {"temperature": 22.0},  # Missing humidity
            {"humidity": 50.0},  # Missing temperature
        ]

        device.update_data(data_points, _USER_SETTINGS)

        # Temperature: (20.0 + 22.0 + 0.0) / 3 = 14.0
        # Humidity: (40.0 + 0.0 + 50.0) / 3 = 30.0
        assert device.temperature == 14.0
        assert device.humidity == 30.0

    def test_update_data_sets_timestamp(self):
        """Test that update_data sets the timestamp from the last data point."""
        device = Device({})

        data_points = [
            {"temperature": 20.0, "timestamp": 1000},
            {"temperature": 22.0, "timestamp": 2000},
            {"temperature": 24.0, "timestamp": 3000},
        ]

        device.update_data(data_points, _USER_SETTINGS)

        assert device.timestamp == 3000

    def test_update_data_all_sensor_fields(self):
        """Test update_data with all sensor fields."""
        device = Device({})

        data_points = [
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
            }
        ]

        device.update_data(data_points, _USER_SETTINGS)

        # Check a few fields
        assert device.virus_index == 2.5
        assert device.mold_index == 1.8
        assert device.temperature == 22.5
        assert device.humidity == 45.0
        assert device.pm25 == 12.3
        assert device.tvoc == 150.0
        assert device.co2 == 800.0
        assert device.co == 0.5


class TestDeviceAttributeNames:
    """Test attribute name conversion."""

    def test_to_attr_name_conversion(self):
        """Test _to_attr_name method."""
        device = Device({})

        # Test camelCase to snake_case conversion
        assert device._to_attr_name("virusIndex") == "virus_index"
        assert device._to_attr_name("pm25") == "pm25"  # No conversion needed
        assert device._to_attr_name("airPressure") == "air_pressure"
        assert device._to_attr_name("deviceName") == "device_name"
        assert device._to_attr_name("serialNumber") == "serial_number"

    def test_sensor_fields_attributes(self):
        """Test that all sensor fields have corresponding attributes."""
        device = Device({})

        for field in Device.SENSOR_FIELDS:
            attr_name = device._to_attr_name(field)
            assert hasattr(device, attr_name)
            # Initial value should be 0.0
            assert getattr(device, attr_name) == 0.0
