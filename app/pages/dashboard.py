import sys
sys.path.append('../scripts/')

import datetime
import pdb
import streamlit as st
import pandas as pd
import time
import asyncio  
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sensor_simulation import iot_sensor
from helpers import get_percentage_change,generate_color_dict
from streamlit_folium import folium_static
import folium 

# from folium.plugins import Realtime
# from folium.utilities import JsCode
# import threading

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Container for real-time updates
placeholder = st.empty()
# --------------------------------------------------------------------------------------------------------------------------

#@st.cache_resource
def initiate_sensor(seed=1, data= None):
    """ Function for caching the sensor objects 
    `data`: Data to be passed to the sensor as initial."""

    if data:
        sensor = iot_sensor(seed=seed)
        sensor.set_stored_data(data)
    else: sensor = iot_sensor(seed=seed)
    return sensor 

def return_df_from_sensor(generate_new=True,seed=1, data= None,p=1):
    """Function to modularize better the extraction and instances of sensors being simulated.
    `generate_new (Bool)`: Calls the generation method of the sensor class to append a new line of data.
    """

    if data: sensor = initiate_sensor(seed=seed,data=data) # Load the sensor 
    else: sensor = initiate_sensor(seed=seed,data=None)
    
    if generate_new: 
        sensor.generate_sensor_data(p_change=p)
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

def display_hist_dist_chart(container, df,selected_var,**kwargs):
    """Function to make the line chart.
    Assumes a df is handed. Checks for numeric columns to be plotted. 
    `x_col`: Searches for a variable to be plotted against.
    """
    # Create distplot with custom bin_size
    data = [df.loc[:,i].values.tolist() for i in df.columns if i in selected_var]
    fig = ff.create_distplot(data, selected_var, bin_size=kwargs.get("bin_size",0.5),colors=kwargs.get("colors"))

    container.plotly_chart(fig)

def display_line_chart(container, df, selected_var, x_col = "datetime" , **kwargs):
    """Function to make the line chart.
    Assumes a df is handed. Checks for numeric columns to be plotted. 
    `x_col`: Searches for a variable to be plotted against.
    """
    # Create an empty list to store traces
    traces = []

    # Loop through selected variables and create traces
    for variable in selected_var:
        trace = go.Scatter(x=df[x_col], y=df[variable], mode='lines', name=variable,
                           line=dict(color=kwargs.get("colors")[variable]))
        traces.append(trace)

    # Create layout
    layout = go.Layout(
        title=None,
        xaxis=dict(title='Time', color='white'),
        yaxis=dict(title=f'{selected_var}', color='white'),
        plot_bgcolor='rgba(0,0,0,0)'
)

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    fig.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)',showlegend=True)

    # Display the chart
    container.plotly_chart(fig)

def display_ml_results(html_file):
    
    with open(html_file,"r") as file: html=file.read()
    st.html(html)

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

        if "colors_dict" not in st.session_state:     
            st.session_state.colors_dict = generate_color_dict(df_.columns)

        # st.sidebar.title("Navigation")
        # tabs = ["Dash","Map"]
        # self.selected_tab = st.sidebar.radio("Go to", tabs)

        # Initialize Streamlit session state
        if 'last_loc' not in st.session_state:
            st.session_state.last_loc = pd.DataFrame({'latitude': [23.120153640967356],
                                                    'longitude': [-82.32292555767346]})
            
        self.map = folium.Map(location=[*df_.location.iloc[-1].values()],zoom_start=17)

        with self.placeholder.container():

            self.col1, self.col2 = st.columns([1,4])

            with self.col1:
                with st.expander("📈 Metrics",expanded=True):
                    self.metrics = st.empty()
                
                with st.expander("💻 Forecast ",expanded=True):
                    st.image("brain.png")
                    display_ml_results(html_file="ml_widget.html")

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

                with st.expander(label="Graph"):
                    self.line_chart = st.empty()
                    self.hist_chart = st.empty()

            st.sidebar.checkbox("Autorefresh", 
                                help="Hacer que mapa se actualice automáticamente",
                                value=False,
                                key="autorefresh")

            st.sidebar.slider(label="Seleccionar tasa de refresco de mapa",
                              min_value=1,max_value=10,
                              disabled=not st.session_state.autorefresh,key="run_every")

            self.map_fragment()

            with st.expander("Revieved Data"):
                self.df_display = st.empty()
            
    async def realtime_dashboard(self):

        #await self.update_folium_map()

        if "df" not in st.session_state:
            df = return_df_from_sensor(generate_new=False,data=None,p=0.5)
        if "df" in st.session_state:
            data = st.session_state.df.to_dict(orient='records')

            df = return_df_from_sensor(generate_new=True,data=data,p=0.5)

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

        with self.placeholder.container():

            with self.col1:
                # Update metrics 
                display_metrics(self.metrics.container(),self.kpi)

            with self.df_display:

                st.dataframe(df)

            with self.col2:

                var = [var for var,on in st.session_state.variables.items() if on is True]
                display_line_chart(self.line_chart,df,selected_var=var,colors=st.session_state.colors_dict)

                if var:
                    display_hist_dist_chart(self.hist_chart,df,selected_var=var,
                                            bin_size=0.4,colors=[val for key,val in st.session_state.colors_dict.items() if key in var])

            #with self.map_space.container(): 

            self.kpi = {k: v[::-1] for k, v in self.kpi.items()}

        asyncio.sleep(3)

    @st.experimental_fragment(run_every=st.session_state.get("run_every"))                   
    def map_fragment(self):

        with st.expander("Map 🗺",expanded=False):
            #self.map_space  = st.columns([4,1])
            st.button(
            "Update", disabled=not st.session_state.autorefresh)

            self.map_space = st.empty()
    
    async def update_folium_map(self):

        if st.session_state.running or st.session_state.get("df") is not None:

            # Get query params to trigger updates
            lat = st.query_params.get("latitude")
            lon = st.query_params.get("longitude")
            time_sensor = st.query_params.get("time")

            get_speed = st.session_state.df.speed.iloc[-1]

            list_of_pos = [list(pair.values()) for pair in st.session_state.df.location]
            
            trajectory = folium.PolyLine(list_of_pos,
                                        weight=2,
                                        opacity=0.75)

            if not lat and not lon: 
                
                lat,lon = (23.1588114225629,-82.35733509718557)

            # Add markers for the start and end points
            start_marker = folium.Marker(
                location=list_of_pos[0],
                popup=f'Start at {st.session_state.df.datetime.iloc[0]}',
                icon=folium.Icon(color='green', icon='play')
            )

            icon = folium.DivIcon(
            icon_size=(15, 15),
            icon_anchor=(15, 15),
            html = f'<div style="font-size: 8; color: black; width: 40px; height: 40px; text-align: center; line-height: 40px; border-radius: 80%; background: radial-gradient(circle at center, transparent 60%, red 40%, red 100%);"><b>{get_speed}</b></div>'
            )

            position = folium.Marker(location=[lat,lon],tooltip=f"{time_sensor}",icon=icon)

            self.map.location = [lat, lon]

            self.fg = folium.FeatureGroup(name="Markers")
            
            self.fg.add_child(start_marker) # add trajectory
            self.fg.add_child(trajectory)   # add start point
            self.fg.add_child(position)     # add endpoint
            self.map.add_child(self.fg)

            with self.map_space:
                if st.session_state.get("run_every"):
                    folium_static(self.map,width=800,height=1000)

        else: pass

        await asyncio.sleep(3)


        # if st.session_state.auto_refresh: 
        #     time.sleep(3)
        #     st.rerun() 
        # elif st.session_state.refresh:
        #     st.rerun()

        
async def main():

    app = app_structure()

    while st.session_state.running:
        await asyncio.gather(app.realtime_dashboard(),app.update_folium_map())

    

#----------------------------------------------------------------------------------------

if __name__ =="__main__":

    asyncio.run(main())
    #app.update_folium_map()


     






