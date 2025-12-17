# Satellite Trajectory Predictor

A Python-based tool for predicting and plotting satellite orbital trajectories using orbital mechanics principles.

## Team Members

- **Rashika Sugganahalli Natesh Babu** (rsuggana@stevens.edu)
- **Behnam Nejati** (bnejati@stevens.edu)

## Problem Description

This project addresses the real-world engineering problem of predicting satellite orbital trajectories. Understanding and visualizing satellite paths is crucial for:

- **Space mission planning**: Determining optimal launch windows and orbital insertion points
- **Collision avoidance**: Predicting potential collisions between satellites and space debris
- **Communication scheduling**: Planning ground station contacts and satellite passes
- **Space debris tracking**: Monitoring orbital paths of defunct satellites and debris
- **Scientific research**: Studying orbital dynamics and space weather effects

The program reads satellite orbital parameters, performs trajectory calculations using orbital mechanics, and generates visualizations to help users understand and analyze satellite motion.

## Program Structure

```
satellite_trajectory_predictor/
├── main.ipynb                    # Main Jupyter Notebook (entry point)
├── satellite.py                  # Satellite class definition
├── trajectory_plotter.py         # TrajectoryPlotter class (composition with Satellite)
├── orbital_mechanics.py          # Orbital calculation functions
├── data_handler.py               # Data I/O functions
├── animation.py                  # BONUS: Interactive orbit animation module
├── tests/
│   ├── test_satellite.py        # Pytest tests for Satellite class
│   └── test_orbital_mechanics.py # Pytest tests for orbital functions
├── data/
│   ├── sample_satellites.csv    # Sample satellite data
│   └── satellite_summary.csv    # Generated output (created at runtime)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## How to Use the Program

### Prerequisites

- Python 3.12 or 3.13
- Jupyter Notebook
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd satellite_trajectory_predictor
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - NumPy (>=1.24.0) - For numerical calculations and arrays
   - Matplotlib (>=3.7.0) - For plotting and visualization
   - Pytest (>=7.4.0) - For running tests
   - Pandas (>=2.0.0) - For data manipulation (if needed)

### Running the Main Program

1. **Launch Jupyter Notebook**
   ```bash
   jupyter notebook
   ```

2. **Open `main.ipynb`** in the Jupyter interface

3. **Run cells sequentially** (either by clicking "Run All" or running cells one by one)

   The notebook will:
   - Read satellite data from `data/sample_satellites.csv`
   - Create Satellite objects
   - Predict trajectories
   - Generate 2D and 3D visualizations
   - Demonstrate all Part 1 and Part 2 requirements of this project

### Running Tests

To run the test suite:

```bash
pytest tests/
```

To run with verbose output:

```bash
pytest tests/ -v
```

To run a specific test file:

```bash
pytest tests/test_satellite.py
pytest tests/test_orbital_mechanics.py
```

### Using the Modules Programmatically

You can also import and use the modules in your own Python scripts:

```python
from satellite import Satellite
from trajectory_plotter import TrajectoryPlotter
from orbital_mechanics import predict_future_positions
from data_handler import read_satellite_data_from_file, create_satellite_objects
from datetime import datetime

# Read data
data = read_satellite_data_from_file('data/sample_satellites.csv')
satellites = create_satellite_objects(data)

# Use a satellite
iss = satellites[0]
print(iss)

# Predict positions
time_points, positions = predict_future_positions(iss, time_hours=24, resolution_minutes=10)

# Create plots
plotter = TrajectoryPlotter(iss)
fig = plotter.plot_2d_trajectory(time_points)
```

## Features

### Bonus work: Interactive Orbit Animation in 3D

The project includes an **interactive animation feature** that allows users to:
- **Select any satellite** from the loaded dataset
- **Choose simulation duration** (0.5 to 24 hours)
- **Watch a real-time 3D animation** of the satellite orbiting Earth
- **Multi-satellite comparison** - view ISS, Hubble, and Starlink simultaneously

The animation features:
- Smooth 3D visualization with rotating camera
- Satellite trail showing recent orbital path
- Real-time display of elapsed time
- Earth rendered as a 3D sphere

### Core Components

1. **Satellite Class** (`satellite.py`)
   - Represents a satellite with orbital parameters
   - Calculates position at any given time
   - Supports operator overloading for comparisons
   - Includes `__str__` method for readable output

2. **TrajectoryPlotter Class** (`trajectory_plotter.py`)
   - Uses composition relationship with Satellite
   - Creates 2D and 3D trajectory visualizations
   - Generates altitude-over-time plots
   - Handles matplotlib figure creation and styling

3. **Orbital Mechanics Functions** (`orbital_mechanics.py`)
   - `calculate_orbital_elements()`: Parses TLE data
   - `predict_future_positions()`: Generates position predictions
   - `generate_position_generator()`: Generator function for memory-efficient position calculation
   - `calculate_orbital_period()`: Computes orbital period
   - `calculate_velocity()`: Calculates orbital velocity

4. **Data Handler** (`data_handler.py`)
   - `read_satellite_data_from_file()`: Reads CSV files with exception handling
   - `create_satellite_objects()`: Converts data dictionaries to Satellite objects
   - `write_results_to_file()`: Writes results to CSV files

## Requirements Checklist and Verification

### Part 1 Requirements 

- **Two classes with relationship**: `Satellite` and `TrajectoryPlotter` (composition relationship)
- **Two meaningful functions**: `calculate_orbital_elements()` and `predict_future_positions()`
- **Two advanced libraries**: NumPy (orbital calculations) and Matplotlib (visualization)
- **Exception handling**: Two approaches implemented:
  - Try-except blocks in data I/O functions (FileNotFoundError, ValueError)
  - Type checking with TypeError in class constructors
- **Pytest tests**: Comprehensive test suites in `tests/test_satellite.py` and `tests/test_orbital_mechanics.py`
- **Data I/O**: CSV file reading and writing in `data_handler.py`
- **Control flow**: 
  - For loops: Used throughout (e.g., processing satellite data)
  - While loops: Used in `predict_future_positions()` and generator function
  - If statements: Used extensively for validation and conditional logic
- **Docstrings and comments**: All classes and functions have docstrings and meaningful comments
- **README file**: This comprehensive documentation

### Part 2 Requirements 

- **Special functions**: 
  - `enumerate()`: Used in notebook to index satellites
  - `map()`: Used with lambda to calculate altitudes
  - `zip()`: Used to combine satellite names and IDs
  - `filter()`: Used with lambda to filter low-altitude satellites
  - `lambda`: Used with map and filter functions
- **Comprehensions**: 
  - List comprehension: Used extensively (e.g., `[sat.name for sat in satellites]`)
  - Dictionary comprehension: Used to create satellite dictionaries
  - Set comprehension: Used to get unique inclinations
- **Built-in modules**: 
  - `csv`: For reading/writing CSV files
  - `datetime`: For handling time and epoch calculations
  - `sys`: For system-specific parameters
  - `os`: For file system operations
  - `json`: Demonstrated in notebook
- **Mutable and Immutable objects**:
  - Mutable: `list`, `dict` (demonstrated in notebook)
  - Immutable: `str`, `tuple`, `float`, `int` (demonstrated in notebook)
- **Operator overloading**: 
  - `__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__` implemented in Satellite class
  - Allows comparison of satellites by altitude
- **Generator function**: `generate_position_generator()` in `orbital_mechanics.py`
- **`__name__ == "__main__"`**: Demonstrated in notebook
- **`__str__` method**: Implemented in both `Satellite` and `TrajectoryPlotter` classes

## Main Contributions

### Rashika Sugganahalli Natesh Babu
- Contributed to developing a physics model for Satellite and Orbital mechanics - orbit propagation.

### Behnam Nejati
- Contributed to developing test cases and trajectory calculations with 3D plottig.

## Data Source

The project uses sample satellite data stored in `data/sample_satellites.csv` downloaded from celestrak.org. This includes:
- International Space Station (ISS)
- Hubble Space Telescope
- GPS satellites
- Starlink satellites
- Tiangong Space Station

All data uses realistic orbital parameters based on publicly available information. User can add more satellites by following the CSV format:

```csv
name,id,inclination,eccentricity,semi_major_axis,mean_anomaly,epoch
Satellite Name,Satellite ID,Inclination (deg),Eccentricity,Semi-major Axis (km),Mean Anomaly (deg),YYYY-MM-DD HH:MM:SS
```

## Technical Details

### Orbital Mechanics

The program implements **realistic elliptical orbit mechanics** including:

- **Kepler's Equation**: Solved using Newton's method iteration
  - M = E - e·sin(E), where M is mean anomaly, E is eccentric anomaly, e is eccentricity
  
- **True Anomaly Calculation**: From eccentric anomaly using:
  - tan(ν/2) = √((1+e)/(1-e)) · tan(E/2)
  
- **Orbital Radius**: Using the orbit equation:
  - r = a(1-e²)/(1 + e·cos(ν))
  
- **3D Coordinate Transformation**: From perifocal frame to ECI frame using:
  - RAAN (Ω): Right Ascension of Ascending Node
  - Inclination (i): Orbital plane tilt  
  - Argument of Perigee (ω): Orientation within orbital plane

- **Vis-Viva Equation**: For accurate velocity at any orbital position:
  - v = √(μ(2/r - 1/a))

- **Earth Gravitational Parameter**: μ = 398600.4418 km³/s²

This implementation provides realistic orbital trajectories for satellites with any eccentricity between 0 (circular) and nearly 1 (highly elliptical).

### Coordinate System

- Origin: Earth's center
- X-axis: Points along the satellite's initial position vector
- Y-axis: Perpendicular to X in the orbital plane
- Z-axis: Perpendicular to the orbital plane

## Testing

The project includes comprehensive pytest tests covering:
- Satellite creation and validation
- Position calculations
- Operator overloading
- Orbital mechanics functions
- Exception handling

Run tests with:
```bash
pytest tests/ -v
```

## Future Enhancements

Potential improvements for future versions:
- Integration with real-time TLE data sources (e.g., CelesTrak API)
- Support for multi-body orbital mechanics (perturbations)
- Ground track visualization on world map
- Collision prediction algorithms

## License

This project is for educational purposes as part of the AAI/CPE/EE 551 course. 

## Acknowledgments

- Orbital mechanics principles based on standard astrodynamics textbooks
- Sample satellite data based on publicly available information

## Contact

For questions or issues, please contact:
- Rashika Sugganahalli Natesh Babu: rsuggana@stevens.edu
- Behnam Nejati: bnejati@stevens.edu
