# generate_sensor_data

import random
import time 
import math
from datetime import datetime, timedelta
from helpers import generate_vector_components

class iot_sensor:

    def __init__(self,seed = 1234) -> None:
        """seed = seed for random number generation. Helpful for simulating different sensor. """

        random.seed(seed)                                         # place the seed 
        self.sensor_data_store = []                               # Initialize an empty list to store sensor data
        self.generate_sensor_data()                               # generate initial data points

    def generate_sensor_data(self,p_change=0.5) -> dict:
        '''
        This function generates a simulated data point representing sensor readings. It takes into account the time difference from the last recorded data point to smooth out transitions between consecutive data points. The function uses the previous data, if available, or default values to calculate the new sensor data. The key variables include:

        SENSOR_VARIABLES
        `datetime`: The timestamp of the data point.
        `temperature`: Simulated temperature reading with a slight variation.
        `humidity`: Simulated humidity reading with a slight variation.
        `pressure`: Simulated pressure reading with a slight variation.
        `location`: Simulated location based on the speed and time difference from the previous data point.
        `speed`: Simulated speed with a slight variation.
        
        
        '''
        current_time = datetime.now()

        # Retrieve the latest stored data or use default values
        previous_data = self.sensor_data_store[-1] if self.sensor_data_store else {
            "datetime": current_time - timedelta(seconds=5),
            "temperature": 25.0,
            "humidity": 50.0,
            "pressure": 1005.0,
            "location": {"latitude": 23.1288114225629,"longitude" :-82.37505913042698},
            "speed": 0.0,
        }

        # Calculate time difference
        time_diff = (current_time - previous_data["datetime"]).total_seconds()

        # Smoothly transition values

        # Create a more stable version 

        if random.random() <= p_change:
            temperature = previous_data["temperature"] + random.uniform(-0.5, 0.5)
            humidity = previous_data["humidity"] + random.uniform(-1.0, 1.0)
            pressure = previous_data["pressure"] + random.uniform(-0.5, 0.5)
        else:
            temperature = previous_data["temperature"]
            humidity = previous_data["humidity"]
            pressure = previous_data["pressure"]

        if random.random() <= 0.35:
            speed = previous_data["speed"] + random.uniform(-4.0, 4.0)
        else: speed = previous_data["speed"]

        speed = max(0,speed) # make sure is above 0

        if speed != 0:

            lat_speed , lon_speed = generate_vector_components(speed)
            # Update location based on speed
            location = {"latitude": previous_data["location"]["latitude"]+lat_speed * 1e-5 * time_diff,
                "longitude": previous_data["location"]["longitude"] + lon_speed * 1e-5 * time_diff}
            
        else: location = {"latitude": previous_data["location"]["latitude"],
                "longitude": previous_data["location"]["longitude"]}

        sensor_data = {
            "datetime": current_time,
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pressure": round(pressure, 2),
            "location": location,
            "speed": abs(round(speed, 2)),
            # Add more variables as needed
        }

        self.sensor_data_store.append(sensor_data) # append 

        return sensor_data

    def generate_time_series_data(self,num_points=10) -> list:

        '''This function generates a time series of simulated sensor data points. It calls generate_sensor_data repeatedly to create a list of data points over a specified number of iterations.
        num_points: Length of time-series that is going to be generated
        '''
        time_series_data = []

        for _ in range(num_points):
            sensor_data = self.generate_sensor_data()
            time_series_data.append(sensor_data)

        return time_series_data
    
    def reset_sensor_data(self):

        """> Reset the data stored on sensor_data_store object <"""

        self.sensor_data_store = [] # empty list

    def set_stored_data(self,data):
        """ Function to set an already initialized data store 
        data -List(dict) : Must be compatible with the structure in method `generate_sensor_data`generate  
        """ 
        self.sensor_data_store = data


