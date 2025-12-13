# A Python-Based Tool for Predicting and Plotting Satellite Trajectories

## Project Overview
In the space industry, it is important to know where a satellite is located and how it moves around the Earth. Predicting and visualizing a satellite’s orbit helps engineers plan satellite communication, avoid collisions, and monitor space activity.
This project focuses on a small but useful part of this task, reading real satellite orbital data, predicting where a satellite will be at different times, and plotting its orbit in 3D. The program will use simple physics formulas and open-source libraries to calculate and show the satellite’s path. This type of prediction is critical for mission planning, satellite tracking, and preventing potential orbital collisions - all key challenges in modern aerospace engineering. 

## Folder Structure
- `data/` → Input datasets (TLE files)
- `tests/` → Unit tests using Pytest
- `satellite.py` → Base Satellite class
- `tracked_satellite.py` → Inherited class with prediction functionality
- `data_loader.py` → Functions for reading TLE files safely
- `orbit_analysis.py` → Functions for analysis and plotting
- `requirements.txt` → Required Python packages
- `main.ipynb` → Jupyter Notebook to run and demonstrate the project

## Data Source
- Public TLE data from [Celestrak](https://celestrak.org/NORAD/elements/)
