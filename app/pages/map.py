
import asyncio
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import folium 
from folium.plugins import Realtime
from folium.utilities import JsCode 

def fetch_df():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame([])
    return st.session_state.df

# Function to continuously update query parameters asynchronously
async def update_query_params():

    ph = st.empty()

    with ph.container():
        while True:
            df = fetch_df()
            await asyncio.sleep(2)  # Adjust the interval as needed
            return df
        
async def main():

    st.write("Map Page")

    initial_coords = [23.120153640967356,-82.32292555767346]
    
    m = folium.Map(location=initial_coords,zoom_start=17)
    df = await (update_query_params())

    js = create_source(df.location.iloc[-1])
    rt = Realtime(js,interval=1000)

    #rt = folium.Marker(location=[df.location.iloc[-1]["latitude"],df.location.iloc[-1]["longitude"]],tooltip=f"{df.datetime.iloc[-1]}",icon=folium.Icon(color="green"))
    rt.add_to(m)

    #st_folium(m,width=1000,height=1000)
    folium_static(m,width=1000,height=1000)

    #st.rerun()

    await asyncio.sleep(1)

def create_source(df):

    source = f"""
        function(responseHandler, errorHandler) {{
            var latitude = {df['latitude']};
            var longitude = {df['longitude']};

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

def update_folium_map(my_map):
        
    # Get query params to trigger updates
    lat = st.query_params.get("latitude")
    lon = st.query_params.get("longitude")
    time_sensor = st.query_params.get("time")

    if not lat and not lon: 
        
        lat,lon = (23.1588114225629,-82.35733509718557)

    js = create_source(pd.DataFrame([{"latitude":lat,"longitude":lon}]))

    rt = Realtime(create_source,interval=1000)
    #rt = folium.Marker(location=[lat,lon],tooltip=f"{time_sensor}",icon=folium.Icon(color="green"))
    rt.add_to(my_map)
    

    #self.fg.add_child(folium.Marker(location=[lat,lon],tooltip=f"{time_sensor}",icon=folium.Icon(color="green")))

    #out = st_folium(self.map,feature_group_to_add=self.fg,width=1200,height=500)   


if __name__ == "__main__":

    st.title("MAP - Sensor ")

    asyncio.run(main())

    