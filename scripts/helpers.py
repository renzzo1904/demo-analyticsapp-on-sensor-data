# Auxiliar functions 
import numpy as np
from typing import List
import math 
import random

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
    # Generate random components for latitude and longitude
    lat_component = random.uniform(-1, 1)
    long_component = random.uniform(-1, 1)
    
    # Calculate the length of the vector
    vector_length = math.sqrt(lat_component**2 + long_component**2)
    
    # Scale the components to match the desired speed
    scaled_lat_component = abs(lat_component / vector_length * speed)
    scaled_long_component = abs(long_component / vector_length * speed)
    
    return scaled_lat_component, scaled_long_component

def generate_color_dict(columns):
    color_dict = {}
    for column in columns:
        # Generate random RGB values
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        # Convert RGB to hexadecimal
        color = '#%02x%02x%02x' % (r, g, b)
        # Assign color to column
        color_dict[column] = color
    return color_dict
