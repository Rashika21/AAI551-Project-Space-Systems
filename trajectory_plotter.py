"""
Module for TrajectoryPlotter class that handles visualization of satellite trajectories.

This module provides the TrajectoryPlotter class which uses composition
to work with Satellite objects and creates various types of plots.
"""

import matplotlib.pyplot as plt
import numpy as np
from satellite import Satellite


class TrajectoryPlotter:
    """
    A class to plot and visualize satellite trajectories.
    
    This class uses composition to work with Satellite objects and creates
    various types of plots for trajectory visualization. The plotter maintains
    a reference to a Satellite object but doesn't inherit from it.
    
    Attributes:
        satellite (Satellite): The satellite object to plot
        fig (matplotlib.figure.Figure): Matplotlib figure object
        ax (matplotlib.axes.Axes): Matplotlib axes object
    """
    
    def __init__(self, satellite):
        """
        Initialize a TrajectoryPlotter with a Satellite object.
        
        Uses composition: TrajectoryPlotter "has-a" Satellite
        
        Args:
            satellite (Satellite): The satellite to plot
            
        Raises:
            TypeError: If satellite is not a Satellite instance
        """
        if not isinstance(satellite, Satellite):
            raise TypeError("satellite must be a Satellite instance")
        self.satellite = satellite
        self.fig = None
        self.ax = None
    
    def plot_2d_trajectory(self, time_points, show_earth=True):
        """
        Plot a smooth 2D trajectory projection in the XY plane.
        
        Args:
            time_points (list): List of time deltas in seconds from epoch
            show_earth (bool): Whether to show Earth as a circle
            smooth (bool): Whether to use interpolation for smooth curve
            
        Returns:
            matplotlib.figure.Figure: The figure object
            
        Raises:
            ValueError: If time_points is empty or invalid
        """
        if not time_points or len(time_points) == 0:
            raise ValueError("time_points cannot be empty")
        
        # Calculate positions for all time points using a for loop
        positions = []
        for t in time_points:
            try:
                pos = self.satellite.calculate_position(t)
                positions.append(pos)
            except ValueError as e:
                print(f"Warning: Skipping invalid time point {t}: {e}")
                continue
        
        if not positions:
            raise ValueError("No valid positions calculated")
        
        positions = np.array(positions)
        
        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        
        # Plot trajectory with smooth line
        self.ax.plot(positions[:, 0], positions[:, 1], 'b-', linewidth=2.5, 
                    label=f'{self.satellite.name} Trajectory', alpha=0.8, linestyle='-')
        
        # Mark start and end points
        self.ax.plot(positions[0, 0], positions[0, 1], 'go', 
                     markersize=12, label='Start', zorder=5, markeredgecolor='darkgreen', markeredgewidth=2)
        self.ax.plot(positions[-1, 0], positions[-1, 1], 'ro', 
                     markersize=12, label='End', zorder=5, markeredgecolor='darkred', markeredgewidth=2)
        
        # Show Earth if requested
        if show_earth:
            earth_radius = 6371  # km
            circle = plt.Circle((0, 0), earth_radius, color='lightblue', 
                              alpha=0.4, label='Earth', edgecolor='blue', linewidth=2.5)
            self.ax.add_patch(circle)
        
        # Set labels and title
        self.ax.set_xlabel('X (km)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y (km)', fontsize=12, fontweight='bold')
        self.ax.set_title(f'2D Trajectory of {self.satellite.name}', 
                         fontsize=14, fontweight='bold')
        self.ax.legend(loc='upper right', fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_aspect('equal')
        
        return self.fig
    
    def plot_3d_trajectory(self, time_points):
        """
        Plot a smooth 3D trajectory visualization.
        
        Args:
            time_points (list): List of time deltas in seconds from epoch
            smooth (bool): Whether to use more points for smoother curve
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # Calculate positions
        positions = []
        for t in time_points:
            pos = self.satellite.calculate_position(t)
            positions.append(pos)
        
        positions = np.array(positions)
        
        # Create 3D figure
        self.fig = plt.figure(figsize=(14, 12))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Plot smooth trajectory (positions already calculated with good resolution)
        self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
                    'b-', linewidth=2.5, alpha=0.8, label=f'{self.satellite.name}')
        
        # Mark start and end points
        self.ax.scatter(positions[0, 0], positions[0, 1], positions[0, 2], 
                       color='green', s=200, label='Start', zorder=5, edgecolors='darkgreen', linewidth=2)
        self.ax.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2], 
                       color='red', s=200, label='End', zorder=5, edgecolors='darkred', linewidth=2)
        
        # Show Earth as a sphere
        earth_radius = 6371
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x_earth = earth_radius * np.outer(np.cos(u), np.sin(v))
        y_earth = earth_radius * np.outer(np.sin(u), np.sin(v))
        z_earth = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        self.ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.25, 
                           color='lightblue', edgecolor='none', linewidth=0)
        
        # Set labels and title
        self.ax.set_xlabel('X (km)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y (km)', fontsize=12, fontweight='bold')
        self.ax.set_zlabel('Z (km)', fontsize=12, fontweight='bold')
        self.ax.set_title(f'3D Trajectory of {self.satellite.name}', 
                         fontsize=14, fontweight='bold')
        self.ax.legend(loc='upper left', fontsize=10)
        
        return self.fig
    
    @staticmethod
    def plot_multiple_3d_trajectories(satellites, time_points, colors=None, labels=None):
        """
        Plot multiple satellite trajectories in the same 3D plot for comparison.
        
        Args:
            satellites (list): List of Satellite objects to plot
            time_points (list): List of time deltas in seconds from epoch
            colors (list): Optional list of colors for each satellite
            labels (list): Optional list of labels (uses satellite names if None)
        
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        if not satellites:
            raise ValueError("At least one satellite must be provided")
        
        # Default colors
        if colors is None:
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
        
        # Default labels
        if labels is None:
            labels = [sat.name for sat in satellites]
        
        # Create 3D figure
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot each satellite trajectory
        for idx, satellite in enumerate(satellites):
            # Calculate positions
            positions = []
            for t in time_points:
                pos = satellite.calculate_position(t)
                positions.append(pos)
            
            positions = np.array(positions)
            
            # Plot smooth trajectory (positions already calculated with good resolution)
            color = colors[idx % len(colors)]
            ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], '-',
                   linewidth=2.5, alpha=0.8, color=color, label=labels[idx])
            
            # Mark start point for each satellite
            ax.scatter(positions[0, 0], positions[0, 1], positions[0, 2],
                      color=color, s=150, marker='o', zorder=5, alpha=0.9, edgecolors='black', linewidth=1.5)
        
        # Show Earth as a sphere
        earth_radius = 6371
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x_earth = earth_radius * np.outer(np.cos(u), np.sin(v))
        y_earth = earth_radius * np.outer(np.sin(u), np.sin(v))
        z_earth = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.2, 
                       color='lightblue', edgecolor='none', linewidth=0)
        
        # Set labels and title
        ax.set_xlabel('X (km)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y (km)', fontsize=12, fontweight='bold')
        ax.set_zlabel('Z (km)', fontsize=12, fontweight='bold')
        ax.set_title('3D Trajectory Comparison - Multiple Satellites', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        
        return fig
    
    def plot_altitude_over_time(self, time_points):
        """
        Plot satellite altitude over time.
        
        Args:
            time_points (list): List of time deltas in seconds from epoch
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        # Calculate positions and convert to altitudes
        altitudes = []
        times_hours = []
        
        for t in time_points:
            pos = self.satellite.calculate_position(t)
            # Calculate distance from origin (altitude + Earth radius)
            distance = np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
            altitude = distance - 6371  # Subtract Earth radius
            altitudes.append(altitude)
            times_hours.append(t / 3600)  # Convert to hours
        
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        # Plot altitude
        self.ax.plot(times_hours, altitudes, 'b-', linewidth=2, label='Altitude')
        self.ax.axhline(y=self.satellite.get_altitude(), color='r', 
                       linestyle='--', alpha=0.5, label='Mean Altitude')
        
        self.ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Altitude (km)', fontsize=12, fontweight='bold')
        self.ax.set_title(f'Altitude Over Time: {self.satellite.name}', 
                         fontsize=14, fontweight='bold')
        self.ax.legend(fontsize=10)
        self.ax.grid(True, alpha=0.3)
        
        return self.fig
    
    def __str__(self):
        """
        String representation of the TrajectoryPlotter.
        
        Returns:
            str: Formatted string with plotter information
        """
        return f"TrajectoryPlotter(satellite='{self.satellite.name}')"
    
    def __repr__(self):
        """Return a developer-friendly string representation."""
        return f"TrajectoryPlotter({repr(self.satellite)})"

