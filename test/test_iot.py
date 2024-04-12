import sys
sys.path.append('../scripts/')

import unittest
import pdb
import numpy as np
import pandas as pd
import pytest
from datetime import datetime
from sensor_simulation import iot_sensor
from helpers import get_percentage_change


#-------------------------------------------------------------------------------------------------
#  TEST HELPERS 

# class TestGetPercentageChange(unittest.TestCase):
    
#     def test_return_str(self):
#         self.assertEqual(get_percentage_change([10, 20]), "100.0%")
#         self.assertEqual(get_percentage_change([20, 10]), "-100.0%")

#     def test_return_float(self):
#         self.assertEqual(get_percentage_change([10, 20], return_str=False), 100.0)
#         self.assertEqual(get_percentage_change([20, 10], return_str=False), -100.0)

#     def test_insufficient_elements(self):
#         with self.assertRaises(IndexError):
#             get_percentage_change([10])

# -------------------------------------------------------------------------------------
# TEST SENSOR CLASS

class TestIoTSensor(unittest.TestCase):

    def setUp(self):
        self.sensor = iot_sensor()

    def test_generate_new_on_setted_data(self):

        data= [{
                "datetime": datetime.now(),
                "temperature": 30,
                "humidity": 1000,
                "pressure": 5,
                "location": {
                    "latitude": 20,
                    "longitude": -60
                },
                "speed": 0
            }]
        
        # Set the data store
        self.sensor.set_stored_data(data)

        self.sensor.generate_sensor_data() # generate a new set of data 

        self.assertEqual(len(self.sensor.sensor_data_store), 2) # Generates one elememt

        elem1, elem2 = [{key: value for key, value in i.items() if key != "datetime"} for i in self.sensor.sensor_data_store] # remove the date which is going to be different
        #pdb.set_trace()
        self.assertFalse(elem1==elem2)

    def test_set_stored_data(self):
        # Given initial data
        data = [
            {
                "datetime": "Timestamp('2024-04-11 16:22:49.576858')",
                "temperature": 25,
                "humidity": 50,
                "pressure": 1005,
                "location": {
                    "latitude": 23.1288114225629,
                    "longitude": -82.37505913042698
                },
                "speed": 0
            }
        ]

        # Set the data store
        self.sensor.set_stored_data(data)

        # Retrieve the stored data
        stored_data = self.sensor.sensor_data_store

        # Assert that the data store has a list of length 2
        self.assertEqual(len(stored_data), 1)

        # Assert that the first element is equal to the initial data
        self.assertEqual(stored_data, data)

    def test_generate_sensor_data(self):
        # Test if generate_sensor_data returns a dictionary
        sensor_data = self.sensor.generate_sensor_data()
        self.assertIsInstance(sensor_data, dict)

        # Test if required keys are present in the generated sensor data
        required_keys = ['datetime', 'temperature', 'humidity', 'pressure','location', 'speed']
        for key in required_keys:
            self.assertIn(key, sensor_data)

    def test_generate_time_series_data(self):
        # Test if generate_time_series_data returns a list
        time_series_data = self.sensor.generate_time_series_data()
        self.assertIsInstance(time_series_data, list)

        # Test if the length of time series data matches the specified number of points
        num_points = 5
        time_series_data = self.sensor.generate_time_series_data(num_points)
        self.assertEqual(len(time_series_data), num_points)

    def test_reset(self):

        self.sensor.reset_sensor_data() # resets sensor
        self.assertEqual(self.sensor.sensor_data_store,[], "List reset does not work")

    def test_df(self):
        # Test if a df can be created from the dict in the __init__ process
        df = pd.DataFrame(self.sensor.sensor_data_store)

        # Insert a breakpoint to inspect values
        self.assertTrue(len(df.columns)>=1," Data Frame does not have columns")
        self.assertTrue(len(df)>=1,"There is no data in the df")

    def test_new_data(self):
        # Test if when called the generate method a new value different than the previous one is appended 
        len1 = len(self.sensor.sensor_data_store)

        # generate one data point 
        self.sensor.generate_sensor_data()

        len2 = len(self.sensor.sensor_data_store)
        e1,e2 = self.sensor.sensor_data_store
        self.assertEqual(len2-len1,1," Generation yields more than one data point ")
        self.assertFalse(e1==e2)

if __name__ == '__main__':
    unittest.main()
