"""
Module for Satellite class that represents a satellite object.

This module provides the Satellite class which stores orbital parameters
and calculates satellite positions using orbital mechanics.
"""

import numpy as np
from datetime import datetime, timedelta


class Satellite:
    """
    A class to represent a satellite and its orbital characteristics.
    
    This class stores satellite information including orbital parameters
    and provides methods to calculate satellite position and predict trajectories.
    The class supports operator overloading for comparison operations.
    
    Attributes:
        name (str): Name of the satellite
        satellite_id (str): Unique identifier for the satellite
        inclination (float): Orbital inclination in degrees
        eccentricity (float): Orbital eccentricity (0-1)
        semi_major_axis (float): Semi-major axis in kilometers
        mean_anomaly (float): Mean anomaly in degrees (at epoch)
        raan (float): Right Ascension of Ascending Node in degrees (Ω)
        argument_of_perigee (float): Argument of perigee in degrees (ω)
        epoch (datetime): Epoch time of the orbital parameters
    """
    
    def __init__(self, name, satellite_id, inclination, eccentricity, 
                 semi_major_axis, mean_anomaly, epoch, raan=0.0, argument_of_perigee=0.0):
        """
        Initialize a Satellite object.
        
        Args:
            name (str): Name of the satellite
            satellite_id (str): Unique identifier
            inclination (float): Inclination in degrees
            eccentricity (float): Eccentricity (0-1)
            semi_major_axis (float): Semi-major axis in km
            mean_anomaly (float): Mean anomaly in degrees (at epoch)
            epoch (datetime): Epoch time
            raan (float): Right Ascension of Ascending Node in degrees (default: 0.0)
            argument_of_perigee (float): Argument of perigee in degrees (default: 0.0)
        
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs with exception handling
        if not isinstance(name, str) or not name:
            raise ValueError("Satellite name must be a non-empty string")
        if not isinstance(satellite_id, str) or not satellite_id:
            raise ValueError("Satellite ID must be a non-empty string")
        
        if not isinstance(inclination, (int, float)) or inclination < 0 or inclination > 180:
            raise ValueError("Inclination must be a number between 0 and 180 degrees")
        if not isinstance(eccentricity, (int, float)) or eccentricity < 0 or eccentricity >= 1:
            raise ValueError("Eccentricity must be a number between 0 and 1")
        if not isinstance(semi_major_axis, (int, float)) or semi_major_axis <= 0:
            raise ValueError("Semi-major axis must be a positive number")
        if not isinstance(mean_anomaly, (int, float)):
            raise ValueError("Mean anomaly must be a number")
        
        if not isinstance(epoch, datetime):
            raise ValueError("Epoch must be a datetime object")
        if not isinstance(raan, (int, float)) or raan < 0 or raan >= 360:
            raise ValueError("RAAN must be a number between 0 and 360 degrees")
        if not isinstance(argument_of_perigee, (int, float)) or argument_of_perigee < 0 or argument_of_perigee >= 360:
            raise ValueError("Argument of perigee must be a number between 0 and 360 degrees")
        
        # Assign attributes
        self.name = name
        self.satellite_id = satellite_id
        self.inclination = float(inclination)
        self.eccentricity = float(eccentricity)
        self.semi_major_axis = float(semi_major_axis)
        self.mean_anomaly = float(mean_anomaly)
        self.raan = float(raan)
        self.argument_of_perigee = float(argument_of_perigee)
        self.epoch = epoch
    
    def solve_kepler_equation(self, mean_anomaly_rad, tolerance=1e-10, max_iterations=100):
        """
        Solve Kepler's equation: M = E - e*sin(E) for eccentric anomaly E.
        
        Uses Newton's method for iterative solution.
        
        Args:
            mean_anomaly_rad (float): Mean anomaly in radians
            tolerance (float): Convergence tolerance
            max_iterations (int): Maximum number of iterations
        
        Returns:
            float: Eccentric anomaly in radians
        """
        # Initial guess: for small eccentricity, E ≈ M
        # For larger e, use better initial guess
        if self.eccentricity < 0.8:
            E = mean_anomaly_rad
        else:
            E = np.pi  # Better initial guess for high eccentricity
        
        # Normalize mean anomaly to [0, 2π]
        mean_anomaly_rad = mean_anomaly_rad % (2 * np.pi)
        
        # Newton's method iteration
        for _ in range(max_iterations):
            # Calculate f(E) = E - e*sin(E) - M
            f = E - self.eccentricity * np.sin(E) - mean_anomaly_rad
            
            # Calculate f'(E) = 1 - e*cos(E)
            f_prime = 1 - self.eccentricity * np.cos(E)
            
            # Update: E_new = E_old - f(E)/f'(E)
            E_new = E - f / f_prime
            
            # Check convergence
            if abs(E_new - E) < tolerance:
                return E_new
            
            E = E_new
        
        return E  # Return last computed value if convergence not reached
    
    def calculate_position(self, time_delta_seconds):
        """
        Calculate satellite position at a given time after epoch.
        
        Uses realistic elliptical orbit mechanics by solving Kepler's equation.
        Implements proper coordinate transformation using orbital elements.
        
        Args:
            time_delta_seconds (float): Time in seconds after epoch
            
        Returns:
            tuple: (x, y, z) coordinates in kilometers (ECI frame)
        
        Raises:
            ValueError: If time_delta_seconds is negative
        """
        if time_delta_seconds < 0:
            raise ValueError("Time delta cannot be negative")
        
        # Earth gravitational parameter (km^3/s^2)
        mu = 398600.4418
        
        # Mean motion (rad/s) - angular velocity
        mean_motion = np.sqrt(mu / (self.semi_major_axis ** 3))
        
        # Mean anomaly at time (initial + change over time)
        mean_anomaly_rad = np.radians(self.mean_anomaly)
        mean_anomaly_at_time = mean_anomaly_rad + mean_motion * time_delta_seconds
        
        # Solve Kepler's equation to get eccentric anomaly
        E = self.solve_kepler_equation(mean_anomaly_at_time)
        
        # Calculate true anomaly from eccentric anomaly
        # tan(ν/2) = sqrt((1+e)/(1-e)) * tan(E/2)
        if self.eccentricity < 1e-10:  # Circular orbit
            nu = E  # True anomaly equals eccentric anomaly for circular orbits
        else:
            sqrt_term = np.sqrt((1 + self.eccentricity) / (1 - self.eccentricity))
            nu = 2 * np.arctan2(sqrt_term * np.sin(E/2), np.cos(E/2))
        
        # Calculate radius from true anomaly
        # r = a(1 - e²) / (1 + e*cos(ν))
        a = self.semi_major_axis
        e = self.eccentricity
        r = a * (1 - e**2) / (1 + e * np.cos(nu))
        
        # Convert to Cartesian coordinates in perifocal frame (PQW frame)
        # where P points to perigee, Q is 90° ahead in orbital plane
        x_pqw = r * np.cos(nu)
        y_pqw = r * np.sin(nu)
        z_pqw = 0.0
        
        # Transform from perifocal frame to ECI frame using rotation matrices
        # Rotation sequence: R_z(ω) * R_x(i) * R_z(Ω)
        omega = np.radians(self.argument_of_perigee)  # Argument of perigee
        i = np.radians(self.inclination)  # Inclination
        Omega = np.radians(self.raan)  # RAAN
        
        # Calculate rotation matrix components
        cos_omega = np.cos(omega)
        sin_omega = np.sin(omega)
        cos_i = np.cos(i)
        sin_i = np.sin(i)
        cos_Omega = np.cos(Omega)
        sin_Omega = np.sin(Omega)
        
        # Apply rotation matrix: R = R_z(Ω) * R_x(i) * R_z(ω)
        # First rotation: R_z(ω) - argument of perigee
        x1 = x_pqw * cos_omega - y_pqw * sin_omega
        y1 = x_pqw * sin_omega + y_pqw * cos_omega
        z1 = z_pqw
        
        # Second rotation: R_x(i) - inclination
        x2 = x1
        y2 = y1 * cos_i - z1 * sin_i
        z2 = y1 * sin_i + z1 * cos_i
        
        # Third rotation: R_z(Ω) - RAAN
        x = x2 * cos_Omega - y2 * sin_Omega
        y = x2 * sin_Omega + y2 * cos_Omega
        z = z2
        
        return (x, y, z)
    
    def get_altitude(self):
        """
        Calculate the mean altitude of the satellite above Earth's surface.
        
        For elliptical orbits, this returns the semi-major axis minus Earth radius,
        which is approximately the mean altitude.
        
        Returns:
            float: Mean altitude in kilometers
        """
        earth_radius = 6371.0  # km
        return self.semi_major_axis - earth_radius
    
    def get_perigee_altitude(self):
        """
        Calculate perigee (lowest point) altitude.
        
        Returns:
            float: Perigee altitude in kilometers
        """
        earth_radius = 6371.0  # km
        perigee_radius = self.semi_major_axis * (1 - self.eccentricity)
        return perigee_radius - earth_radius
    
    def get_apogee_altitude(self):
        """
        Calculate apogee (highest point) altitude.
        
        Returns:
            float: Apogee altitude in kilometers
        """
        earth_radius = 6371.0  # km
        apogee_radius = self.semi_major_axis * (1 + self.eccentricity)
        return apogee_radius - earth_radius
    
    def __str__(self):
        """
        String representation of the Satellite object.
        
        Returns:
            str: Formatted string with satellite information
        """
        altitude = self.get_altitude()
        return (f"Satellite(name='{self.name}', id='{self.satellite_id}', "
                f"inclination={self.inclination:.2f}°, "
                f"eccentricity={self.eccentricity:.6f}, "
                f"altitude={altitude:.2f} km)")
    
    def __repr__(self):
        """Return a developer-friendly string representation."""
        return (f"Satellite('{self.name}', '{self.satellite_id}', "
                f"{self.inclination}, {self.eccentricity}, "
                f"{self.semi_major_axis}, {self.mean_anomaly}, "
                f"{self.raan}, {self.argument_of_perigee}, {self.epoch})")
    
    def __eq__(self, other):
        """
        Operator overloading: equality comparison.
        
        Two satellites are equal if they have the same satellite_id.
        
        Args:
            other: Another Satellite object to compare
            
        Returns:
            bool: True if satellites have same ID, False otherwise
        """
        if not isinstance(other, Satellite):
            return False
        return self.satellite_id == other.satellite_id
    
    def __lt__(self, other):
        """
        Operator overloading: less than comparison.
        
        Compares satellites by their altitude.
        
        Args:
            other: Another Satellite object to compare
            
        Returns:
            bool: True if this satellite's altitude is less than other's
        """
        if not isinstance(other, Satellite):
            raise TypeError(f"Cannot compare Satellite with {type(other)}")
        return self.get_altitude() < other.get_altitude()
    
    def __le__(self, other):
        """Operator overloading: less than or equal comparison."""
        if not isinstance(other, Satellite):
            raise TypeError(f"Cannot compare Satellite with {type(other)}")
        return self.get_altitude() <= other.get_altitude()
    
    def __gt__(self, other):
        """Operator overloading: greater than comparison."""
        if not isinstance(other, Satellite):
            raise TypeError(f"Cannot compare Satellite with {type(other)}")
        return self.get_altitude() > other.get_altitude()
    
    def __ge__(self, other):
        """Operator overloading: greater than or equal comparison."""
        if not isinstance(other, Satellite):
            raise TypeError(f"Cannot compare Satellite with {type(other)}")
        return self.get_altitude() >= other.get_altitude()

