"""
Module containing functions for orbital mechanics calculations.

This module provides utility functions for calculating orbital elements
and predicting future satellite positions.
"""

import numpy as np
from datetime import datetime, timedelta
from satellite import Satellite


def calculate_orbital_elements(tle_data):
    """
    Calculate orbital elements from Two-Line Element (TLE) data or dictionary.
    
    This function parses orbital data and extracts key orbital parameters.
    It can work with simplified dictionary format or parse actual TLE strings.
    
    Args:
        tle_data (dict): Dictionary containing orbital data with keys:
                        - 'inclination': Inclination in degrees
                        - 'eccentricity': Eccentricity (0-1)
                        - 'mean_motion': Mean motion in rev/day (optional)
                        - 'semi_major_axis': Semi-major axis in km (optional)
                        - 'mean_anomaly': Mean anomaly in degrees
                        - 'epoch': Epoch time as string 'YYYY-MM-DD HH:MM:SS'
                        - 'line1', 'line2': Optional TLE lines for parsing
    
    Returns:
        dict: Dictionary containing orbital elements:
              - 'inclination': Inclination in degrees
              - 'eccentricity': Eccentricity
              - 'semi_major_axis': Semi-major axis in km
              - 'mean_anomaly': Mean anomaly in degrees
              - 'epoch': Epoch datetime object
    
    Raises:
        ValueError: If TLE data is invalid or missing required fields
        KeyError: If required keys are missing from dictionary
    """
    try:
        # Check for required fields
        required_fields = ['inclination', 'eccentricity', 'mean_anomaly', 'epoch']
        for field in required_fields:
            if field not in tle_data:
                raise KeyError(f"Missing required field: {field}")
        
        # Extract parameters
        inclination = float(tle_data['inclination'])
        eccentricity = float(tle_data['eccentricity'])
        mean_anomaly = float(tle_data['mean_anomaly'])
        
        # Calculate or extract semi-major axis
        if 'semi_major_axis' in tle_data:
            semi_major_axis = float(tle_data['semi_major_axis'])
        elif 'mean_motion' in tle_data:
            # Calculate from mean motion
            mean_motion = float(tle_data['mean_motion'])  # rev/day
            mu = 398600.4418  # km^3/s^2
            mean_motion_rad_per_sec = mean_motion * 2 * np.pi / 86400
            semi_major_axis = (mu / (mean_motion_rad_per_sec ** 2)) ** (1/3)
        else:
            raise KeyError("Either 'semi_major_axis' or 'mean_motion' must be provided")
        
        # Parse epoch
        epoch_str = tle_data['epoch']
        if isinstance(epoch_str, str):
            epoch = datetime.strptime(epoch_str, '%Y-%m-%d %H:%M:%S')
        elif isinstance(epoch_str, datetime):
            epoch = epoch_str
        else:
            raise ValueError("Epoch must be a string or datetime object")
        
        # Validate values
        if inclination < 0 or inclination > 180:
            raise ValueError("Inclination must be between 0 and 180 degrees")
        if eccentricity < 0 or eccentricity >= 1:
            raise ValueError("Eccentricity must be between 0 and 1")
        
        return {
            'inclination': inclination,
            'eccentricity': eccentricity,
            'semi_major_axis': semi_major_axis,
            'mean_anomaly': mean_anomaly,
            'epoch': epoch
        }
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error parsing orbital data: {str(e)}")


def predict_future_positions(satellite, time_hours=24, resolution_minutes=10, smooth_factor=1):
    """
    Predict satellite positions over a future time period.
    
    Uses a while loop to generate time points and calculates positions.
    
    Args:
        satellite (Satellite): Satellite object to predict positions for
        time_hours (float): Number of hours into the future to predict
        resolution_minutes (float): Time resolution in minutes
        smooth_factor (int): Factor to multiply resolution for smoother curves (default: 1)
    
    Returns:
        tuple: (time_points, positions) where:
               - time_points: List of time deltas in seconds
               - positions: List of (x, y, z) tuples
    
    Raises:
        TypeError: If satellite is not a Satellite instance
        ValueError: If time_hours or resolution_minutes are invalid
    """
    if not isinstance(satellite, Satellite):
        raise TypeError("satellite must be a Satellite instance")
    if time_hours <= 0:
        raise ValueError("time_hours must be positive")
    if resolution_minutes <= 0:
        raise ValueError("resolution_minutes must be positive")
    
    # Adjust resolution for smooth plotting
    effective_resolution = resolution_minutes / smooth_factor
    
    # Generate time points using a while loop
    total_minutes = time_hours * 60
    num_points = int(total_minutes / effective_resolution)
    
    time_points = []
    positions = []
    
    i = 0
    while i < num_points:
        time_delta_seconds = i * effective_resolution * 60
        
        if time_delta_seconds <= time_hours * 3600:  # Don't exceed requested time
            time_points.append(time_delta_seconds)
            pos = satellite.calculate_position(time_delta_seconds)
            positions.append(pos)
        
        i += 1
    
    return time_points, positions


def generate_position_generator(satellite, time_hours=24, resolution_minutes=10):
    """
    Generator function that yields satellite positions over time.
    
    This is a generator function that produces positions on-demand,
    which is memory-efficient for large time ranges.
    
    Args:
        satellite (Satellite): Satellite object
        time_hours (float): Number of hours into the future
        resolution_minutes (float): Time resolution in minutes
    
    Yields:
        tuple: (time_delta_seconds, (x, y, z)) position at that time
    
    Example:
        >>> for time, pos in generate_position_generator(sat, 1, 1):
        ...     print(f"Time: {time}s, Position: {pos}")
    """
    if not isinstance(satellite, Satellite):
        raise TypeError("satellite must be a Satellite instance")
    
    total_seconds = time_hours * 3600
    resolution_seconds = resolution_minutes * 60
    
    current_time = 0
    while current_time <= total_seconds:
        position = satellite.calculate_position(current_time)
        yield (current_time, position)
        current_time += resolution_seconds


def calculate_orbital_period(satellite):
    """
    Calculate the orbital period of a satellite.
    
    Uses Kepler's third law: T = 2π * sqrt(a³/μ)
    
    Args:
        satellite (Satellite): Satellite object
    
    Returns:
        float: Orbital period in seconds
    """
    if not isinstance(satellite, Satellite):
        raise TypeError("satellite must be a Satellite instance")
    
    mu = 398600.4418  # km^3/s^2
    a = satellite.semi_major_axis  # km
    
    period = 2 * np.pi * np.sqrt((a ** 3) / mu)
    return period


def calculate_velocity(satellite, time_delta_seconds=0):
    """
    Calculate the orbital velocity of a satellite at a given time.
    
    Uses the vis-viva equation: v = sqrt(mu * (2/r - 1/a))
    where r is the current radius and a is the semi-major axis.
    
    Args:
        satellite (Satellite): Satellite object
        time_delta_seconds (float): Time after epoch in seconds
    
    Returns:
        float: Velocity in km/s
    """
    if not isinstance(satellite, Satellite):
        raise TypeError("satellite must be a Satellite instance")
    
    # Get current position
    pos = satellite.calculate_position(time_delta_seconds)
    r = np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)  # Current radius
    
    # Vis-viva equation for elliptical orbits: v = sqrt(mu * (2/r - 1/a))
    mu = 398600.4418  # km^3/s^2
    a = satellite.semi_major_axis  # Semi-major axis
    
    velocity = np.sqrt(mu * (2.0 / r - 1.0 / a))
    
    return velocity

