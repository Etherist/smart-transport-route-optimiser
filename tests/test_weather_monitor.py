"""
Unit tests for Weather Monitor Agent
"""

import pytest
from src.agents.weather_monitor import (
    fetch_weather_alerts,
    get_weather_impact_multiplier
)

class TestWeatherMonitor:

    def test_fetch_weather_nsw_northern(self):
        """Test fetching weather alerts for northern NSW."""
        # Coordinates for northern NSW (around Taree/Port Macquarie)
        alerts = fetch_weather_alerts(-31.0, 152.8, 50)

        assert isinstance(alerts, list)
        if alerts:
            assert all("type" in alert for alert in alerts)
            assert all("severity" in alert for alert in alerts)
            assert all("message" in alert for alert in alerts)

    def test_fetch_weather_nsw_central(self):
        """Test fetching weather alerts for central NSW."""
        alerts = fetch_weather_alerts(-33.4, 151.3, 50)

        assert isinstance(alerts, list)

    def test_fetch_weather_nsw_southern(self):
        """Test fetching weather alerts for southern NSW."""
        alerts = fetch_weather_alerts(-35.0, 149.5, 50)

        assert isinstance(alerts, list)

    def test_fetch_weather_with_radius(self):
        """Test that radius parameter is accepted."""
        alerts = fetch_weather_alerts(-33.8688, 151.2093, radius_km=100)

        assert isinstance(alerts, list)

    def test_weather_alert_structure(self):
        """Test that weather alerts have required fields."""
        alerts = fetch_weather_alerts(-33.8688, 151.2093, 50)

        if alerts:  # May be empty depending on location
            required_fields = ["type", "severity", "message", "location"]
            for alert in alerts:
                for field in required_fields:
                    assert field in alert
                assert "lat" in alert["location"]
                assert "lng" in alert["location"]

    def test_get_weather_impact_multiplier(self):
        """Test impact multipliers for different severities."""
        assert get_weather_impact_multiplier("low") == 1.1
        assert get_weather_impact_multiplier("medium") == 1.25
        assert get_weather_impact_multiplier("high") == 1.5
        assert get_weather_impact_multiplier("extreme") == 2.0

    def test_get_weather_impact_multiplier_unknown(self):
        """Test default multiplier for unknown severity."""
        assert get_weather_impact_multiplier("unknown") == 1.0

    def test_fetch_weather_handles_error(self):
        """Test graceful handling when something goes wrong."""
        # The function should return at least an empty list even on error
        alerts = fetch_weather_alerts(0, 0, 50)  # Potentially invalid
        assert isinstance(alerts, list)
