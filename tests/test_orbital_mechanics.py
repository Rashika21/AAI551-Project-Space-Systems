"""
Test module for orbital mechanics functions.

This module contains pytest tests for functions in orbital_mechanics.py.
"""

import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orbital_mechanics import (
    calculate_orbital_elements,
    predict_future_positions,
    generate_position_generator,
    calculate_orbital_period,
    calculate_velocity
)
from satellite import Satellite


class TestOrbitalMechanics:
    """Test class for orbital mechanics functions."""
    
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
            epoch=epoch
        )
    
    @pytest.fixture
    def sample_tle_data(self):
        """Create sample TLE data dictionary."""
        return {
            'inclination': 51.6,
            'eccentricity': 0.0001,
            'mean_motion': 15.54,
            'mean_anomaly': 0.0,
            'epoch': '2024-01-01 00:00:00'
        }
    
    def test_calculate_orbital_elements(self, sample_tle_data):
        """Test orbital elements calculation from TLE data."""
        elements = calculate_orbital_elements(sample_tle_data)
        
        assert 'inclination' in elements
        assert 'eccentricity' in elements
        assert 'semi_major_axis' in elements
        assert 'mean_anomaly' in elements
        assert 'epoch' in elements
        
        assert elements['inclination'] == 51.6
        assert elements['eccentricity'] == 0.0001
        assert isinstance(elements['epoch'], datetime)
        assert elements['semi_major_axis'] > 0
    
    def test_calculate_orbital_elements_with_semi_major_axis(self):
        """Test orbital elements with explicit semi-major axis."""
        tle_data = {
            'inclination': 90.0,
            'eccentricity': 0.001,
            'semi_major_axis': 7000.0,
            'mean_anomaly': 45.0,
            'epoch': '2024-01-01 00:00:00'
        }
        
        elements = calculate_orbital_elements(tle_data)
        assert elements['semi_major_axis'] == 7000.0
    
    def test_calculate_orbital_elements_missing_field(self):
        """Test that missing required field raises ValueError."""
        incomplete_tle = {
            'inclination': 51.6,
            # Missing other required fields
        }
        
        with pytest.raises(ValueError):
            calculate_orbital_elements(incomplete_tle)
    
    def test_calculate_orbital_elements_invalid_inclination(self):
        """Test that invalid inclination raises ValueError."""
        invalid_tle = {
            'inclination': 200,  # Invalid: > 180
            'eccentricity': 0.001,
            'semi_major_axis': 6778.0,
            'mean_anomaly': 0.0,
            'epoch': '2024-01-01 00:00:00'
        }
        
        with pytest.raises(ValueError):
            calculate_orbital_elements(invalid_tle)
    
    def test_predict_future_positions(self, sample_satellite):
        """Test position prediction function."""
        time_points, positions = predict_future_positions(
            sample_satellite, 
            time_hours=1, 
            resolution_minutes=10
        )
        
        # Should have 6 positions (1 hour / 10 minutes = 6)
        assert len(time_points) == len(positions)
        assert len(positions) == 6
        
        # Each position should be a tuple of 3 coordinates
        assert all(len(pos) == 3 for pos in positions)
    
    def test_predict_future_positions_invalid_satellite(self):
        """Test that invalid satellite type raises TypeError."""
        with pytest.raises(TypeError):
            predict_future_positions("not a satellite", time_hours=1)
    
    def test_predict_future_positions_invalid_time(self, sample_satellite):
        """Test that invalid time_hours raises ValueError."""
        with pytest.raises(ValueError):
            predict_future_positions(sample_satellite, time_hours=-1)
        
        with pytest.raises(ValueError):
            predict_future_positions(sample_satellite, time_hours=1, resolution_minutes=-5)
    
    def test_generate_position_generator(self, sample_satellite):
        """Test generator function for positions."""
        generator = generate_position_generator(
            sample_satellite,
            time_hours=0.5,  # 30 minutes
            resolution_minutes=10
        )
        
        # Get first few positions from generator
        positions = []
        count = 0
        for time, pos in generator:
            positions.append((time, pos))
            count += 1
            if count >= 4:  # Get 4 positions
                break
        
        assert len(positions) == 4
        assert all(isinstance(pos, tuple) and len(pos) == 3 for _, pos in positions)
    
    def test_generate_position_generator_invalid_satellite(self):
        """Test that generator raises TypeError for invalid satellite."""
        with pytest.raises(TypeError):
            next(generate_position_generator("not a satellite"))
    
    def test_calculate_orbital_period(self, sample_satellite):
        """Test orbital period calculation."""
        period = calculate_orbital_period(sample_satellite)
        
        # Period should be positive
        assert period > 0
        # For ISS-like orbit (~6778 km), period should be around 92-93 minutes
        # Convert to seconds: ~5500 seconds
        assert 5000 < period < 6000
    
    def test_calculate_velocity(self, sample_satellite):
        """Test velocity calculation."""
        velocity = calculate_velocity(sample_satellite, time_delta_seconds=0)
        
        # Velocity should be positive
        assert velocity > 0
        # For low Earth orbit, velocity should be around 7-8 km/s
        assert 6 < velocity < 9


