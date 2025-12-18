"""
Module for creating animated satellite orbit visualizations.

This module provides functions to create interactive 3D animations
of satellites orbiting Earth, allowing users to visualize orbital motion
in real-time.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from satellite import Satellite

# Set animation embed limit to allow larger animations (100MB)
matplotlib.rcParams['animation.embed_limit'] = 100


def create_orbit_animation(satellite, simulation_hours=2, fps=30, trail_length=50):
    """
    Create an animated 3D visualization of a satellite orbiting Earth.
    
    This function generates a smooth animation showing the satellite's
    position as it moves along its orbital path around Earth.
    
    Args:
        satellite (Satellite): The satellite object to animate
        simulation_hours (float): Duration of simulation in hours
        fps (int): Frames per second for the animation
        trail_length (int): Number of previous positions to show as trail
    
    Returns:
        matplotlib.animation.FuncAnimation: The animation object
    
    Raises:
        TypeError: If satellite is not a Satellite instance
        ValueError: If simulation_hours is not positive
    """
    if not isinstance(satellite, Satellite):
        raise TypeError("satellite must be a Satellite instance")
    if simulation_hours <= 0:
        raise ValueError("simulation_hours must be positive")
    
    # Calculate orbital period to determine appropriate time step
    mu = 398600.4418  # Earth gravitational parameter
    orbital_period = 2 * np.pi * np.sqrt(satellite.semi_major_axis**3 / mu)
    orbital_period_minutes = orbital_period / 60
    
    # Calculate total simulation time
    total_seconds = simulation_hours * 3600
    total_minutes = simulation_hours * 60
    
    # Calculate number of complete orbits in simulation
    num_orbits = total_seconds / orbital_period
    
    # Frame sampling strategy: sample based on orbital period for realistic motion
    # Aim for ~60-120 frames per orbit for smooth animation
    frames_per_orbit = 80  # Good balance between smoothness and file size
    ideal_num_frames = int(frames_per_orbit * num_orbits)
    
    # Cap maximum frames to prevent extremely large animation files
    max_frames = 2000
    if ideal_num_frames > max_frames:
        # If too many orbits, reduce frames per orbit proportionally
        num_frames = max_frames
        frames_per_orbit = max_frames / num_orbits
        # Recalculate to ensure we still cover full simulation time
        if frames_per_orbit < 20:
            frames_per_orbit = 20  # Minimum frames per orbit
            num_frames = int(frames_per_orbit * num_orbits)
            if num_frames > max_frames:
                num_frames = max_frames
    else:
        num_frames = ideal_num_frames
        if num_frames < 60:  # Minimum frames for smooth animation
            num_frames = 60
    
    # Calculate actual fps based on desired playback duration
    # Playback duration should be proportional to simulation time
    # Target: ~1 minute playback per hour of simulation, max 3 minutes
    target_playback_minutes = min(simulation_hours, 3)
    target_playback_seconds = target_playback_minutes * 60
    actual_fps = num_frames / target_playback_seconds
    
    # Ensure fps is reasonable (between 10 and 30)
    if actual_fps < 10:
        actual_fps = 10
        target_playback_seconds = num_frames / actual_fps
    elif actual_fps > 30:
        actual_fps = 30
        target_playback_seconds = num_frames / actual_fps
    
    # Pre-calculate all positions for smooth animation
    # Times array represents actual simulation time from 0 to total_seconds
    times = np.linspace(0, total_seconds, num_frames)
    positions = np.array([satellite.calculate_position(t) for t in times])
    
    # Create figure and 3D axis
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Set up the plot limits based on orbit size
    max_range = satellite.semi_major_axis * 1.3
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # Create Earth sphere
    earth_radius = 6371  # km
    u_earth = np.linspace(0, 2 * np.pi, 50)
    v_earth = np.linspace(0, np.pi, 50)
    x_earth = earth_radius * np.outer(np.cos(u_earth), np.sin(v_earth))
    y_earth = earth_radius * np.outer(np.sin(u_earth), np.sin(v_earth))
    z_earth = earth_radius * np.outer(np.ones(np.size(u_earth)), np.cos(v_earth))
    
    # Plot Earth
    ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.6, 
                   color='lightblue', edgecolor='none')
    
    # Plot full orbital path (faint)
    full_orbit_times = np.linspace(0, orbital_period, 500)
    full_orbit_positions = np.array([satellite.calculate_position(t) for t in full_orbit_times])
    ax.plot(full_orbit_positions[:, 0], full_orbit_positions[:, 1], 
            full_orbit_positions[:, 2], 'gray', alpha=0.3, linewidth=1, 
            label='Orbital Path')
    
    # Initialize satellite marker and trail
    satellite_marker, = ax.plot([], [], [], 'ro', markersize=10, 
                                label=satellite.name, zorder=5)
    trail_line, = ax.plot([], [], [], 'r-', linewidth=2, alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('X (km)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Y (km)', fontsize=11, fontweight='bold')
    ax.set_zlabel('Z (km)', fontsize=11, fontweight='bold')
    
    # Time display text
    time_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                         fontweight='bold', color='darkblue')
    info_text = ax.text2D(0.02, 0.90, '', transform=ax.transAxes, fontsize=10,
                         color='darkgreen')
    
    ax.legend(loc='upper right', fontsize=10)
    
    def init():
        """Initialize animation."""
        satellite_marker.set_data([], [])
        satellite_marker.set_3d_properties([])
        trail_line.set_data([], [])
        trail_line.set_3d_properties([])
        time_text.set_text('')
        info_text.set_text('')
        return satellite_marker, trail_line, time_text, info_text
    
    def animate(frame):
        """Update animation frame."""
        # Current position
        x, y, z = positions[frame]
        
        # Update satellite marker
        satellite_marker.set_data([x], [y])
        satellite_marker.set_3d_properties([z])
        
        # Update trail (last trail_length positions)
        start_idx = max(0, frame - trail_length)
        trail_x = positions[start_idx:frame+1, 0]
        trail_y = positions[start_idx:frame+1, 1]
        trail_z = positions[start_idx:frame+1, 2]
        trail_line.set_data(trail_x, trail_y)
        trail_line.set_3d_properties(trail_z)
        
        # Update time display - shows actual simulation time
        current_time = times[frame]
        hours = int(current_time // 3600)
        minutes = int((current_time % 3600) // 60)
        seconds = int(current_time % 60)
        time_text.set_text(f'Simulation Time: {hours:02d}h {minutes:02d}m {seconds:02d}s')
        
        # Calculate orbits completed and current altitude
        orbits_completed = current_time / orbital_period
        distance = np.sqrt(x**2 + y**2 + z**2)
        altitude = distance - earth_radius
        info_text.set_text(f'Altitude: {altitude:.1f} km | Orbits: {orbits_completed:.2f} / {num_orbits:.2f}')
        
        # Update title with orbital period information
        ax.set_title(f'{satellite.name} Orbit Animation\n'
                    f'Simulation: {simulation_hours:.1f}h ({num_orbits:.1f} orbits) | '
                    f'Orbital Period: {orbital_period_minutes:.1f} min',
                    fontsize=14, fontweight='bold')
        
        # Rotate view slightly for dynamic effect
        ax.view_init(elev=20, azim=(30 + frame * 0.1) % 360)
        
        return satellite_marker, trail_line, time_text, info_text
    
    # Create animation with adjusted fps
    anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames,
                        interval=1000/actual_fps, blit=False, repeat=True)
    
    plt.tight_layout()
    return anim, fig


def create_multi_satellite_animation(satellites, simulation_hours=2, fps=30, trail_length=50):
    """
    Create an animated 3D visualization of multiple satellites orbiting Earth.
    
    Args:
        satellites (list): List of Satellite objects to animate
        simulation_hours (float): Duration of simulation in hours
        fps (int): Frames per second for the animation
        trail_length (int): Number of previous positions to show as trail
    
    Returns:
        matplotlib.animation.FuncAnimation: The animation object
    """
    if not satellites:
        raise ValueError("At least one satellite must be provided")
    
    # Calculate simulation parameters with orbital period-based frame sampling
    mu = 398600.4418  # Earth gravitational parameter
    total_seconds = simulation_hours * 3600
    
    # Calculate average orbital period for all satellites (use first satellite as reference)
    # For multi-satellite, we'll use the average orbital period
    avg_orbital_period = np.mean([2 * np.pi * np.sqrt(sat.semi_major_axis**3 / mu) 
                                   for sat in satellites])
    avg_orbital_period_minutes = avg_orbital_period / 60
    
    # Calculate number of complete orbits in simulation (using average)
    num_orbits = total_seconds / avg_orbital_period
    
    # Frame sampling strategy: sample based on orbital period for realistic motion
    frames_per_orbit = 80  # Good balance between smoothness and file size
    ideal_num_frames = int(frames_per_orbit * num_orbits)
    
    # Cap maximum frames to prevent extremely large animation files
    max_frames = 2000
    if ideal_num_frames > max_frames:
        num_frames = max_frames
        frames_per_orbit = max_frames / num_orbits
        if frames_per_orbit < 20:
            frames_per_orbit = 20
            num_frames = int(frames_per_orbit * num_orbits)
            if num_frames > max_frames:
                num_frames = max_frames
    else:
        num_frames = ideal_num_frames
        if num_frames < 60:
            num_frames = 60
    
    # Calculate actual fps based on desired playback duration
    target_playback_minutes = min(simulation_hours, 3)
    target_playback_seconds = target_playback_minutes * 60
    actual_fps = num_frames / target_playback_seconds
    
    # Ensure fps is reasonable (between 10 and 30)
    if actual_fps < 10:
        actual_fps = 10
        target_playback_seconds = num_frames / actual_fps
    elif actual_fps > 30:
        actual_fps = 30
        target_playback_seconds = num_frames / actual_fps
    
    # Times array represents actual simulation time from 0 to total_seconds
    times = np.linspace(0, total_seconds, num_frames)
    
    # Pre-calculate all positions for all satellites
    all_positions = {}
    for sat in satellites:
        all_positions[sat.name] = np.array([sat.calculate_position(t) for t in times])
    
    # Create figure
    fig = plt.figure(figsize=(14, 11))
    ax = fig.add_subplot(111, projection='3d')
    
    # Determine plot limits
    max_sma = max(sat.semi_major_axis for sat in satellites)
    max_range = max_sma * 1.3
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # Create Earth
    earth_radius = 6371
    u_earth = np.linspace(0, 2 * np.pi, 50)
    v_earth = np.linspace(0, np.pi, 50)
    x_earth = earth_radius * np.outer(np.cos(u_earth), np.sin(v_earth))
    y_earth = earth_radius * np.outer(np.sin(u_earth), np.sin(v_earth))
    z_earth = earth_radius * np.outer(np.ones(np.size(u_earth)), np.cos(v_earth))
    ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.5, 
                   color='lightblue', edgecolor='none')
    
    # Colors for different satellites
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta']
    
    # Initialize markers and trails for each satellite
    markers = {}
    trails = {}
    
    for idx, sat in enumerate(satellites):
        color = colors[idx % len(colors)]
        marker, = ax.plot([], [], [], 'o', color=color, markersize=10, 
                         label=sat.name, zorder=5)
        trail, = ax.plot([], [], [], '-', color=color, linewidth=2, alpha=0.6)
        markers[sat.name] = marker
        trails[sat.name] = trail
    
    # Labels
    ax.set_xlabel('X (km)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Y (km)', fontsize=11, fontweight='bold')
    ax.set_zlabel('Z (km)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    
    time_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                         fontweight='bold', color='darkblue')
    
    def init():
        for sat in satellites:
            markers[sat.name].set_data([], [])
            markers[sat.name].set_3d_properties([])
            trails[sat.name].set_data([], [])
            trails[sat.name].set_3d_properties([])
        time_text.set_text('')
        return list(markers.values()) + list(trails.values()) + [time_text]
    
    def animate(frame):
        for sat in satellites:
            positions = all_positions[sat.name]
            x, y, z = positions[frame]
            
            # Update marker
            markers[sat.name].set_data([x], [y])
            markers[sat.name].set_3d_properties([z])
            
            # Update trail
            start_idx = max(0, frame - trail_length)
            trail_x = positions[start_idx:frame+1, 0]
            trail_y = positions[start_idx:frame+1, 1]
            trail_z = positions[start_idx:frame+1, 2]
            trails[sat.name].set_data(trail_x, trail_y)
            trails[sat.name].set_3d_properties(trail_z)
        
        # Update time - shows actual simulation time
        current_time = times[frame]
        hours = int(current_time // 3600)
        minutes = int((current_time % 3600) // 60)
        seconds = int(current_time % 60)
        time_text.set_text(f'Simulation Time: {hours:02d}h {minutes:02d}m {seconds:02d}s')
        
        # Calculate orbits completed (using average orbital period)
        orbits_completed = current_time / avg_orbital_period
        
        ax.set_title(f'Multi-Satellite Orbit Animation\n'
                    f'Simulation: {simulation_hours:.1f}h ({num_orbits:.1f} orbits) | '
                    f'Satellites: {len(satellites)} | Avg Period: {avg_orbital_period_minutes:.1f} min',
                    fontsize=14, fontweight='bold')
        
        ax.view_init(elev=20, azim=(30 + frame * 0.1) % 360)
        
        return list(markers.values()) + list(trails.values()) + [time_text]
    
    # Create animation with adjusted fps
    anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames,
                        interval=1000/actual_fps, blit=False, repeat=True)
    
    plt.tight_layout()
    return anim, fig


def interactive_satellite_selector(satellites_data):
    """
    Display available satellites and let user select one.
    
    Args:
        satellites_data: List of satellite data dictionaries or Satellite objects
    
    Returns:
        int: Index of selected satellite
    """
    print("\n" + "=" * 50)
    print("Available Satellites:")
    print("=" * 50)
    
    for idx, sat in enumerate(satellites_data, 1):
        if isinstance(sat, Satellite):
            name = sat.name
            altitude = sat.get_altitude()
        else:
            name = sat.get('name', 'Unknown')
            altitude = sat.get('semi_major_axis', 6778) - 6371
        print(f"  {idx}. {name} (Altitude: {altitude:.1f} km)")
    
    print("=" * 50)
    
    while True:
        try:
            choice = int(input(f"\nSelect satellite (1-{len(satellites_data)}): "))
            if 1 <= choice <= len(satellites_data):
                return choice - 1
            print(f"Please enter a number between 1 and {len(satellites_data)}")
        except ValueError:
            print("Please enter a valid number")


def get_simulation_hours():
    """
    Get simulation duration from user input.
    
    Returns:
        float: Number of hours for simulation
    """
    print("\n" + "=" * 50)
    print("Simulation Duration")
    print("=" * 50)
    print("Recommended: 1-24 hours")
    print("(1 hour = ~1 orbit for LEO satellites)")
    
    while True:
        try:
            hours = float(input("\nEnter simulation hours (0.5 - 48): "))
            if 0.5 <= hours <= 48:
                return hours
            print("Please enter a value between 0.5 and 48 hours")
        except ValueError:
            print("Please enter a valid number")


if __name__ == "__main__":
    # Demo animation
    from datetime import datetime
    
    print("Satellite Orbit Animation Demo")
    print("=" * 50)
    
    # Create a sample satellite
    demo_sat = Satellite(
        name="ISS",
        satellite_id="25544",
        inclination=51.6444,
        eccentricity=0.0001647,
        semi_major_axis=6778.14,
        mean_anomaly=45.2,
        epoch=datetime(2024, 1, 1),
        raan=238.5,
        argument_of_perigee=112.0
    )
    
    print(f"Animating: {demo_sat.name}")
    print(f"Altitude: {demo_sat.get_altitude():.2f} km")
    
    anim, fig = create_orbit_animation(demo_sat, simulation_hours=1.5, fps=20)
    plt.show()

