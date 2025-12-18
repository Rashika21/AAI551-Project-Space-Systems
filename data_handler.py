"""
Module for handling data input/output operations.

This module provides functions to read satellite data from files
and write results to output files.
"""

import csv
from datetime import datetime
from typing import List, Dict, Optional
from satellite import Satellite


def read_satellite_data_from_file(filename):
    """
    Read satellite data from a CSV file.
    
    The CSV file should have the following columns:
    name, id, inclination, eccentricity, semi_major_axis, mean_anomaly, raan, argument_of_perigee, epoch
    
    Args:
        filename (str): Path to the CSV data file
    
    Returns:
        list: List of dictionaries containing satellite data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
        ValueError: If the file format is invalid
    """
    try:
        satellites = []
        with open(filename, 'r', encoding='utf-8') as file:
            # Read CSV file
            reader = csv.DictReader(file)
            
            # Check for required columns
            required_columns = ['name', 'id', 'inclination', 'eccentricity', 
                              'semi_major_axis', 'mean_anomaly', 'epoch']
            
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV file must contain columns: {required_columns}")
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Parse epoch string to datetime
                    epoch = datetime.strptime(row['epoch'], '%Y-%m-%d %H:%M:%S')
                    
                    # Get RAAN and argument_of_perigee if present, default to 0.0
                    raan = float(row.get('raan', 0.0))
                    argument_of_perigee = float(row.get('argument_of_perigee', 0.0))
                    
                    satellite_data = {
                        'name': row['name'].strip(),
                        'id': row['id'].strip(),
                        'inclination': float(row['inclination']),
                        'eccentricity': float(row['eccentricity']),
                        'semi_major_axis': float(row['semi_major_axis']),
                        'mean_anomaly': float(row['mean_anomaly']),
                        'raan': raan,
                        'argument_of_perigee': argument_of_perigee,
                        'epoch': epoch
                    }
                    satellites.append(satellite_data)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row {row_num}: {e}")
                    continue
        
        if not satellites:
            raise ValueError("No valid satellite data found in file")
        
        return satellites
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found. Please check the file path.")
    except IOError as e:
        raise IOError(f"Error reading file '{filename}': {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error reading file '{filename}': {str(e)}")


def create_satellite_objects(satellite_data_list):
    """
    Create Satellite objects from a list of satellite data dictionaries.
    
    Args:
        satellite_data_list (list): List of dictionaries containing satellite data
    
    Returns:
        list: List of Satellite objects
    
    Raises:
        ValueError: If no valid satellites can be created
    """
    satellites = []
    errors = []
    
    for idx, sat_data in enumerate(satellite_data_list):
        try:
            sat = Satellite(
                name=sat_data['name'],
                satellite_id=sat_data['id'],
                inclination=sat_data['inclination'],
                eccentricity=sat_data['eccentricity'],
                semi_major_axis=sat_data['semi_major_axis'],
                mean_anomaly=sat_data['mean_anomaly'],
                epoch=sat_data['epoch'],
                raan=sat_data.get('raan', 0.0),
                argument_of_perigee=sat_data.get('argument_of_perigee', 0.0)
            )
            satellites.append(sat)
        except (ValueError, KeyError) as e:
            errors.append(f"Satellite {idx + 1} ({sat_data.get('name', 'unknown')}): {e}")
            continue
    
    if errors:
        print("Warnings while creating satellites:")
        for error in errors:
            print(f"  - {error}")
    
    if not satellites:
        raise ValueError("No valid Satellite objects could be created")
    
    return satellites


def write_results_to_file(filename, data, headers=None):
    """
    Write results to a CSV file.
    
    Args:
        filename (str): Output file path
        data (list): List of data rows (each row is a list)
        headers (list, optional): List of column headers
    
    Raises:
        IOError: If there's an error writing to the file
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers)
            writer.writerows(data)
        print(f"Results successfully written to '{filename}'")
    except IOError as e:
        raise IOError(f"Error writing to file '{filename}': {str(e)}")


def write_satellite_summary_to_file(filename, satellites):
    """
    Write a summary of satellites to a CSV file.
    
    Args:
        filename (str): Output file path
        satellites (list): List of Satellite objects
    """
    headers = ['Name', 'ID', 'Inclination (deg)', 'Eccentricity', 
               'Semi-major Axis (km)', 'Altitude (km)', 'Mean Anomaly (deg)']
    
    data = []
    for sat in satellites:
        row = [
            sat.name,
            sat.satellite_id,
            f"{sat.inclination:.4f}",
            f"{sat.eccentricity:.6f}",
            f"{sat.semi_major_axis:.2f}",
            f"{sat.get_altitude():.2f}",
            f"{sat.mean_anomaly:.2f}"
        ]
        data.append(row)
    
    write_results_to_file(filename, data, headers)

