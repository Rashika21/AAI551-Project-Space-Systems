"""
Test module for Satellite class.

This module contains pytest tests for the Satellite class including
constructor validation, position calculations, and operator overloading.
"""

import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from satellite import Satellite


class TestSatellite:
    """Test class for Satellite functionality."""
    
    @pytest.fixture
    def sample_satellite(self):
        """Create a sample satellite for testing."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        return Satellite(
            name="TestSat",
            satellite_id="12345",
            inclination=51.6,
            eccentricity=0.001,
            semi_major_axis=6778.0,
            mean_anomaly=0.0,
            epoch=epoch,
            raan=0.0,
            argument_of_perigee=0.0
        )
    
    def test_satellite_creation(self, sample_satellite):
        """Test creating a Satellite object with valid parameters."""
        assert sample_satellite.name == "TestSat"
        assert sample_satellite.satellite_id == "12345"
        assert sample_satellite.inclination == 51.6
        assert sample_satellite.eccentricity == 0.001
        assert sample_satellite.semi_major_axis == 6778.0
        assert sample_satellite.mean_anomaly == 0.0
    
    def test_satellite_invalid_name(self):
        """Test that invalid name raises ValueError."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            Satellite(
                name="",  # Empty name
                satellite_id="12345",
                inclination=51.6,
                eccentricity=0.001,
                semi_major_axis=6778.0,
                mean_anomaly=0.0,
                epoch=epoch,
                raan=0.0,
                argument_of_perigee=0.0
            )
    
    def test_satellite_invalid_eccentricity(self):
        """Test that invalid eccentricity raises ValueError."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        
        # Test eccentricity >= 1
        with pytest.raises(ValueError, match="Eccentricity"):
            Satellite(
                name="TestSat",
                satellite_id="12345",
                inclination=51.6,
                eccentricity=1.5,  # Invalid: > 1
                semi_major_axis=6778.0,
                mean_anomaly=0.0,
                epoch=epoch,
                raan=0.0,
                argument_of_perigee=0.0
            )
        
        # Test negative eccentricity
        with pytest.raises(ValueError, match="Eccentricity"):
            Satellite(
                name="TestSat",
                satellite_id="12345",
                inclination=51.6,
                eccentricity=-0.1,  # Invalid: negative
                semi_major_axis=6778.0,
                mean_anomaly=0.0,
                epoch=epoch,
                raan=0.0,
                argument_of_perigee=0.0
            )
    
    def test_satellite_invalid_semi_major_axis(self):
        """Test that invalid semi-major axis raises ValueError."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        
        with pytest.raises(ValueError, match="Semi-major axis"):
            Satellite(
                name="TestSat",
                satellite_id="12345",
                inclination=51.6,
                eccentricity=0.001,
                semi_major_axis=-1000,  # Invalid: negative
                mean_anomaly=0.0,
                epoch=epoch,
                raan=0.0,
                argument_of_perigee=0.0
            )
    
    def test_calculate_position(self, sample_satellite):
        """Test position calculation."""
        pos = sample_satellite.calculate_position(0)
        
        # Position should be a tuple of 3 floats
        assert isinstance(pos, tuple)
        assert len(pos) == 3
        assert all(isinstance(coord, (int, float)) for coord in pos)
    
    def test_calculate_position_negative_time(self, sample_satellite):
        """Test that negative time raises ValueError."""
        with pytest.raises(ValueError, match="Time delta cannot be negative"):
            sample_satellite.calculate_position(-100)
    
    def test_get_altitude(self, sample_satellite):
        """Test altitude calculation."""
        altitude = sample_satellite.get_altitude()
        expected = 6778.0 - 6371.0  # semi_major_axis - Earth radius
        assert abs(altitude - expected) < 0.01
    
    def test_str_representation(self, sample_satellite):
        """Test string representation of satellite."""
        str_repr = str(sample_satellite)
        assert "TestSat" in str_repr
        assert "12345" in str_repr
        assert isinstance(str_repr, str)
    
    def test_equality_operator(self, sample_satellite):
        """Test equality operator overloading."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        same_sat = Satellite(
            name="DifferentName",
            satellite_id="12345",  # Same ID
            inclination=90.0,
            eccentricity=0.5,
            semi_major_axis=8000.0,
            mean_anomaly=180.0,
            epoch=epoch,
            raan=0.0,
            argument_of_perigee=0.0
        )
        
        different_sat = Satellite(
            name="TestSat",
            satellite_id="99999",  # Different ID
            inclination=51.6,
            eccentricity=0.001,
            semi_major_axis=6778.0,
            mean_anomaly=0.0,
            epoch=epoch,
            raan=0.0,
            argument_of_perigee=0.0
        )
        
        assert sample_satellite == same_sat  # Same ID
        assert sample_satellite != different_sat  # Different ID
    
    def test_less_than_operator(self, sample_satellite):
        """Test less than operator overloading (compares by altitude)."""
        epoch = datetime(2024, 1, 1, 0, 0, 0)
        higher_sat = Satellite(
            name="HigherSat",
            satellite_id="99999",
            inclination=51.6,
            eccentricity=0.001,
            semi_major_axis=8000.0,  # Higher altitude
            mean_anomaly=0.0,
            epoch=epoch,
            raan=0.0,
            argument_of_perigee=0.0
        )
        
        assert sample_satellite < higher_sat
        assert higher_sat > sample_satellite
        assert sample_satellite <= higher_sat
        assert higher_sat >= sample_satellite
    
    def test_comparison_with_non_satellite(self, sample_satellite):
        """Test that comparison with non-Satellite raises TypeError."""
        with pytest.raises(TypeError):
            _ = sample_satellite < "not a satellite"
        
        with pytest.raises(TypeError):
            _ = sample_satellite > 123

