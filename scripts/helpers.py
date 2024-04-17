# Auxiliar functions 
import numpy as np
from typing import List
import math 
import random


def km_per_hour_to_lat_lon_velocity(v_km_x, v_km_y, latitude):
    """Function to convert velocity from km/h to lat and lon velocities
    `v_km_per_x`: Velocity in horizontal axis ( longitude ).
    `v_km_per_y`: Velocity in vertical axis ( latitude ).
    `latitude`: Latitude at which the conversion is made.
    """
    # Convert velocity from km/h to km/s (or any other unit of time)
    v_km_per_second_lat = v_km_y / 3600
    v_km_per_second_lon = v_km_y/ (3600 * np.cos(np.radians(latitude)))
    
    # Convert velocity from km/s to lat and lon velocities
    v_lat_per_second = v_km_per_second_lat / 110.574          # 1 degree of latitude = ~110.574 km
    v_lon_per_second = v_km_per_second_lon / (111.32 * 1000)  # 1 degree of longitude = ~111.32 km at equator
    
    return v_lat_per_second, v_lon_per_second

def polar_to_cartesian(radius, theta):
    """Function to simulate circular movement."""
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x, y

def get_percentage_change(my_list, return_str=True):
    """
    Calculates the percentage change between the last two elements of a list.

    Args:
        my_list (List[float]): A list of numeric values.
        return_str (bool, optional): Whether to return the result as a string with a percentage sign. Defaults to True.

    Returns:
        str: The percentage change (rounded to 2 decimal places) or "nd%" if division by zero occurs.
    """
    if my_list[-2] == 0: return "nd%"
    try:
        # Calculate the percentage change
        p = round((my_list[-1] - my_list[-2]) * 100 / my_list[-2], 2)

        # Return as a string with a percentage sign if requested
        if return_str:
            return str(p)+ "%"
        else:
            return p

    except IndexError:
        return "The elements in the list are not sufficient to perform the operation."
 
def generate_vector_components(speed):
    """
    Generates random components for latitude and longitude and scales them to match the desired speed.

    Args:
        speed (float): The desired speed.

    Returns:
        Tuple[float, float]: Scaled latitude and longitude components.
    """
    # Generate random polar coordinates
    radius = speed
    angle = np.random.uniform(0, 2 * np.pi)
    
    # Convert polar coordinates to Cartesian coordinates
    dx, dy = polar_to_cartesian(radius, angle)
    
    # Scale the components to match the desired speed
    scaled_lat_component = dy  
    scaled_long_component = dx  
    
    return scaled_lat_component, scaled_long_component

def generate_color_dict(columns):
    color_dict = {}
    for column in columns:
        # Generate random RGB values
        r = random.randint(20, 255)
        g = random.randint(0, 255)
        b = random.randint(20, 255)
        # Convert RGB to hexadecimal
        color = '#%02x%02x%02x' % (r, g, b)
        # Assign color to column
        color_dict[column] = color
    return color_dict
