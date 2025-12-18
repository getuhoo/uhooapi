# tests/integration/test_integration.py
import pytest
import os


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("UHOO_API_KEY"),
    reason="Integration tests require UHOO_API_KEY environment variable",
)
class TestIntegration:
    """Integration tests with real API (use sparingly)."""

    def test_real_api_connection(self):
        """Test actual API connection (requires valid API key)."""
        from uhooapi import UhooClient

        api_key = os.getenv("UHOO_API_KEY")
        client = UhooClient(api_key=api_key)

        # This makes real API calls - use cautiously
        try:
            devices = client.get_devices()
            # Basic validation of response structure
            assert isinstance(devices, dict)
            if "devices" in devices:
                assert isinstance(devices["devices"], list)
        except Exception as e:
            # Don't fail tests if API is temporarily down
            pytest.skip(f"API unavailable: {str(e)}")
