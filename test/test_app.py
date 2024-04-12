import sys
sys.path.append('../app/pages')

import streamlit as st
import pdb
import time
from random import randint
import pandas as pd
from datetime import datetime

from dashboard import initiate_sensor, return_df_from_sensor

data =  [{
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

def test_initiate_sensor_with_no_data_different_stores():

    sensor1 = initiate_sensor(seed=randint(0,100),data=None)
    sensor2 = initiate_sensor(seed=randint(0,100),data=None)

    #print(sensor1.sensor_data_store)
    #print(sensor2.sensor_data_store)

    sensor1.generate_sensor_data(p_change=1)
    sensor2.generate_sensor_data(p_change=1)
    #pdb.set_trace()
    sensor1.sensor_data_store = [{key: value for key, value in i.items() if key != "datetime"} for i in sensor1.sensor_data_store ]
    sensor2.sensor_data_store = [{key: value for key, value in i.items() if key != "datetime"} for i in sensor2.sensor_data_store ]

    # test that they generate different second values
    assert sensor1.sensor_data_store[0]!=sensor1.sensor_data_store[1]
    assert sensor2.sensor_data_store[0]!=sensor2.sensor_data_store[1]
    assert sensor1.sensor_data_store[1]!=sensor2.sensor_data_store[1]
    #passed

def test_initiate_sensor_with_data():

    global data

    sensor = initiate_sensor(seed=randint(0,100),data=data)  
    assert len(sensor.sensor_data_store)==1
    assert sensor.sensor_data_store==data
    #pdb.set_trace()
    #passed

def test_return_df_from_sensor_with_data_generate_false():

    global data 

    df= return_df_from_sensor(seed=randint(0,100),generate_new=False,data=data)
    assert df.shape[0]==1
    assert df.iloc[-1].to_dict()==data[0]
    #passed

def test_return_df_from_sensor_without_data_generate_true():

    df = return_df_from_sensor(seed=randint(0,100),generate_new=True,data=None,p=1)
    elem1, elem2 = [{key: value for key, value in i.items() if key != "datetime"} for i in df.to_dict(orient="records")]

    assert df.shape[0]==2
    assert elem1!=elem2
    #passed

def test_return_df_from_sensor_with_data_generate_true():

    global data 

    df= return_df_from_sensor(seed=randint(0,100),generate_new=True,data=data,p=1)
    elem1, elem2 = [{key: value for key, value in i.items() if key != "datetime"} for i in df.to_dict(orient="records")]  # remove the date which is going to be different
    
    assert df.shape[0]==2
    assert df.iloc[-2].to_dict()==data[0]
    assert elem1!=elem2
    #passed