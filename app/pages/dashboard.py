import sys
sys.path.append('../scripts/')

import threading
import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sensor_simulation import iot_sensor
from helpers import get_percentage_change
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import folium 
from folium.plugins import Realtime
from folium.utilities import JsCode



st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Container for real-time updates
placeholder = st.empty()
# --------------------------------------------------------------------------------------------------------------------------

@st.cache_resource
def initiate_sensor(seed=1, data= None):
    """ Function for caching the sensor objects 
    `data`: Data to be passed to the sensor as initial."""

    if data:
        sensor = iot_sensor(seed=seed).set_stored_data(data) 
    else: sensor = iot_sensor(seed=seed)
    return sensor 

def return_df_from_sensor(generate_new=True,seed=1, data= None):
    """Function to modularize better the extraction and instances of sensors being simulated.
    `generate_new (Bool)`: Calls the generation method of the sensor class to append a new line of data.
    """

    if data is None:
        sensor = initiate_sensor(seed=seed) # Load the sensor 
    else: 
        sensor = initiate_sensor(seed=seed,data=data) # Load the sensor 

    if generate_new: 
        sensor.generate_sensor_data()
        return pd.DataFrame(sensor.sensor_data_store)
    else: return pd.DataFrame(sensor.sensor_data_store)

def button_logic():
    """ Button logic for initiating the simulation. """

    # Initialize simulation state
    if 'running' not in st.session_state:  # Creating a dictionary element if it doesn't exist
        st.session_state['running'] = False

    st.markdown("### Simulation Control")

    buttons= st.columns(3)
    with buttons[0]:
        # Button to start the simulation
        if not st.session_state['running']:
            if st.button("Start Simulation"):
                st.session_state['running'] = True
                st.write("")
    with buttons[1]:
        # Button to stop the simulation and refresh the page
        if st.button("Pause"):
            st.session_state['running'] = False
            st.rerun()  # Refreshes the Streamlit app
    with buttons[2]:
        if st.button("Refresh Data"):
            st.session_state['running'] = False
            st.cache_resource.clear()
            st.rerun()

def display_metrics(container,kpi):
    """ Function to modularize the container content.
    `container`: Streamlit container where this function is used. Assumes a st.container() or st.empty()
    """
    with container:
        with st.expander("📈 Metrics",expanded=True):

            #kpi1,kpi2,kpi3,kpi4,kpi5 = st.columns(5) # Create the space for displaying kpis

            st.metric(label="Mean Humidity 💧 ", 
                        value=round(kpi['Mean Humidity'][1]), delta=get_percentage_change(kpi["Mean Humidity"]) )
            st.metric(label="Min Temperature ❄ ", 
                        value=round(kpi['Min Temperature'][1]), delta=get_percentage_change(kpi["Min Temperature"] ))
            st.metric(label="Max Temperature 🔥 ",
                        value=round(kpi['Max Temperature'][1]), delta=get_percentage_change(kpi["Max Temperature"] ))
            st.metric(label="Mean Pressure 💢 ", 
                        value=round(kpi['Mean Pressure'][1]), delta=get_percentage_change(kpi["Mean Pressure"] ))
            st.metric(label="Speed 👟 ", 
                        value=round(kpi['Current Speed'][1]), delta=get_percentage_change(kpi["Current Speed"] ),delta_color="off")

def display_scale_graph(container,data,size_1=150,size_2=40, lowest = 0, highest= 40):


    """ Function to display last value on a Color Scale on. Can be used on temperature, speed or others.

    container: Streamlit container where this function is used. Assumes a st.container() or st.empty()
    data: assumes a data point is handed
    size_1: Controls the size of the first scatter
    size_2: Controls the size of the pointer.
    lowest: Controls the lowest value.
    highest: Controls the highest value. 

    """

    x = pd.Series([0.01*i for i in range(100)])
    x = x * (highest - lowest) + lowest

    y = ["0"]*100

    fig = go.Figure()

    fig.add_trace(go.Bar(y=y, x=x, marker=dict(color=x, colorscale="turbo", showscale=False),
                            hoverinfo=None))

    # Add scatter point at the middle
    fig.add_trace(go.Scatter(x=[data-5], y=[0], marker=dict(color="white", size=size_2,symbol='triangle-up'),
                             line=dict(width=10, color='black'), mode='markers'))

    fig.update_traces(marker_line_width=0, text=None)  # Remove borders and text
    fig.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)',showlegend=False)  # Hide the color scale and set background color

    # Add centered title in white bold
    #fig.update_layout(title=dict(text="Temperature", font=dict(color="black", size=16, family="Arial"),x=0.5, y=0.95, xanchor='center', yanchor='top'))

    fig.update_layout(    xaxis=dict(
        showticklabels=False,  # Hide tick labels
        showgrid=False  # Hide gridlines
    ),
    yaxis=dict(
        showticklabels=False,  # Hide tick labels
        showgrid=False  # Hide gridlines
    ),
    showlegend=False  # Hide legend
)
    container.plotly_chart(fig,use_container_width=True)

def display_line_chart(container, df, selected_var, x_col = "datetime" , size=30):
    """Function to make the line chart.
    Assumes a df is handed. Checks for numeric columns to be plotted. 
    x_col: Searches for a variable to be plotted against.
    """
    # Create an empty list to store traces
    traces = []

    # Loop through selected variables and create traces
    for variable in selected_var:
        trace = go.Scatter(x=df[x_col], y=df[variable], mode='lines', name=variable)
        traces.append(trace)

    # Create layout
    layout = go.Layout(
        title=None,
        xaxis=dict(title='X Axis', color='white'),
        yaxis=dict(title='Y Axis', color='white'),
        plot_bgcolor='rgba(0,0,0,0)'
)

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    fig.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)',showlegend=False)

    # Display the chart
    container.plotly_chart(fig)

def create_map(data,color=[255, 0, 0]):
    """Function to wrap around the creation of a custom st.pydeck_chart.
    data: Assumes a df with longitude and latitude. Expected to be only one data point.
    color: RGB code to marker on map.
    """
    
    # Simulate sensor location
    sensor_location = data  # Havana, Cuba

    # Create a PyDeck scatterplot layer for the sensor location
    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["longitude", "latitude"],
        get_color=[255, 0, 0],
        get_radius=1000,
    )

    # Create a PyDeck deck with the specified map style and layers
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "zoom": 10,
            "pitch": 50,
        },
        layers=[layer],
    )

    # Display the PyDeck chart using st.pydeck_chart
    return deck

def create_source(df):

    source = f"""
        function(responseHandler, errorHandler) {{
            var latitude = {df['latitude'].values[0]};
            var longitude = {df['longitude'].values[0]};

            var feature = {{
                'type': 'FeatureCollection',
                'features': [{{
                    'type': 'Feature',
                    'geometry': {{
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    }},
                    'properties': {{
                        'id': 'data'
                    }}
                }}]
            }};

            responseHandler(feature);
        }}
    """
    return folium.JsCode(source)

# --------------------------------------------------------------------------------------------------------------------------

class app_structure():

    def __init__(self,placeholder = st.empty()) -> None:

        #-----------------------------------------------------------------------------------------
        button_logic() 

        df_ = return_df_from_sensor(generate_new=False)
        self.kpi = {'Mean Humidity': [0,0], 
            'Min Temperature': [0,0],
            'Max Temperature': [0,0],
            'Mean Pressure': [0,0],
            'Current Speed': [0,0]}                             # Helpful to track changes 

        self.placeholder = st.empty()

        st.sidebar.title("Navigation")
        tabs = ["Map","Dash"]
        self.selected_tab = st.sidebar.radio("Go to", tabs)

                    # Initialize Streamlit session state
        if 'last_loc' not in st.session_state:
            st.session_state.last_loc = pd.DataFrame({'latitude': [23.120153640967356],
                                                    'longitude': [-82.32292555767346]})
            
        self.map = folium.Map(location=[*df_.location.iloc[-1].values()],zoom_start=17)
        #self.fg = folium.FeatureGroup(name="Markers")

        if self.selected_tab == "Dash":

            with self.placeholder.container():

                self.col1, self.col2 = st.columns([1,3])

                with self.col1:

                    self.metrics = st.empty()

                with self.col2: 

                    self.numeric_columns = [col for col in df_.columns if 
                    not any(isinstance(val, (list, dict, tuple)) for val in df_[col]) and
                        df_[col].dtypes not in ["O","<M8[ns]"]]
                    
                    if "variables" not in st.session_state:
                        st.session_state.variables = {}
                    if "last_loc" not in st.session_state:
                        st.session_state["last_loc"] = df_.location.iloc[-1]

                    toogle_widgets_spaces = st.columns(len(self.numeric_columns))

                    for i,col in enumerate(self.numeric_columns):
                        with toogle_widgets_spaces[i]:
                            st.session_state.variables[col]= st.toggle(col,key=col)

                    self.line_chart = st.empty()

                with st.expander("Revieved Data"):
                    self.df_display = st.empty()

        if self.selected_tab == "Map":

            self.map_space  = st.empty()

            #st.rerun()
            
    def realtime_dashboard(self):

        while st.session_state.running:

            if "df" not in st.session_state:
                df = return_df_from_sensor(generate_new=False)
            if "df" in st.session_state:
                data = st.session_state.df.to_dict(orient='records')
                df = return_df_from_sensor(generate_new=True,data=data)

            st.session_state.df = df 
            
            st.query_params["latitude"] = df.location.iloc[-1]["latitude"]
            st.query_params["longitude"] = df.location.iloc[-1]["longitude"]
            st.query_params["time"] = df.datetime.iloc[-1]

            # Calculate KPIs
            self.kpi['Mean Humidity'][1] = df['humidity'].mean()
            self.kpi['Min Temperature'][1] = df['temperature'].min()
            self.kpi['Max Temperature'][1] = df['temperature'].max()
            self.kpi['Mean Pressure'][1] = df['pressure'].mean()
            self.kpi['Current Speed'][1] = df['speed'].iloc[-1]

            self.update_folium_map()

            with self.placeholder.container():

                if self.selected_tab == "Map":

                    with self.map_space.container(): folium_static(self.map,width=800,height=1000)
                     
                if self.selected_tab == "Dash":

                    with self.col1:

                        # Update metrics 
                        display_metrics(self.metrics.container(),self.kpi)

                    with self.df_display:

                        st.dataframe(df)

                    with self.col2:

                        with st.expander(label="Graph"):
                            
                            display_line_chart(self.line_chart,df,selected_var=[var for var,on in st.session_state.variables.items() if on is True]) 

                    self.kpi = {k: v[::-1] for k, v in self.kpi.items()}

            time.sleep(1)
                            
    def update_folium_map(self):
        
        # Get query params to trigger updates
        lat = st.query_params.get("latitude")
        lon = st.query_params.get("longitude")
        time_sensor = st.query_params.get("time")

        if not lat and not lon: 
            
            lat,lon = (23.1588114225629,-82.35733509718557)

        #js = create_source(pd.DataFrame([{"latitude":lat,"longitude":lon}]))

        #rt = Realtime(create_source,interval=1000)
        rt = folium.Marker(location=[lat,lon],tooltip=f"{time_sensor}",icon=folium.Icon(color="green"))
        rt.add_to(self.map)

        #self.fg.add_child(folium.Marker(location=[lat,lon],tooltip=f"{time_sensor}",icon=folium.Icon(color="green")))

        #out = st_folium(self.map,feature_group_to_add=self.fg,width=1200,height=500)      

#----------------------------------------------------------------------------------------

if __name__ =="__main__":

    app_structure().realtime_dashboard()


     






