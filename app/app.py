import streamlit as st

st.set_page_config(
    page_title="IOT Sensor Demo",
    page_icon="✅",
    layout="wide"
)

st.write("# Welcome to ConexIA Dash Demo! 👋")

st.sidebar.success("Select a topic above.")

st.markdown(
    """

# Visión General
¡Bienvenido a la demostración de nuestra Aplicación de Sensores IoT! 
Esta aplicación muestra las capacidades de nuestra tecnología de sensores de última generación 
para el Internet de las Cosas (IoT). Ya sea que seas un desarrollador, un entusiasta de la tecnología 
o alguien curioso sobre el futuro de los dispositivos inteligentes, esta demostración está diseñada 
para darte un vistazo al potencial de los sensores IoT.

    **👈 Selecciona la opción de Dashboard!
    ### Una vez alli solo presiona el botón para comenzar la simulación y voilà!, tienes una idea de 
        una etapa temprana de una solución orientada a manejar los datos obtenidos mediante un dispositivo IoT.
"""
)