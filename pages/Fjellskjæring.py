import streamlit as st
import math

# Define the user inputs
st.title('OBS! Under arbeid. Ikkje testa. Skjeringstabilitet')

V = st.number_input('Volume of the block (m^3)', value=0.0)
rho = st.number_input('Density of the rock (kg/m^3)', value=0.0)
g = 9.81  # Acceleration due to gravity (m/s^2) is constant
a = st.number_input('Seismic acceleration effect (m/s^2)', value=0.0)
A = st.number_input('Area of the fracture surface (m^2)', value=0.0)
U = st.number_input('Force from water pressure in the fracture (kN)', value=0.0)
beta = st.number_input('Angle of inclination of the fracture plane (degrees)', value=0.0)
alpha = st.number_input('Angle between the bolt and the fracture plane (degrees)', value=0.0)
phi = st.number_input('Friction angle of the fracture (degrees)', value=0.0)
c = st.number_input('Cohesion of the fracture plane (kN/m^2)', value=0.0)
T = st.number_input('Total bolt force (kN)', value=0.0)
B = st.number_input('Bolt’s bearing capacity (yield strength) (kN)', value=0.0)
N = st.number_input('Number of bolts', value=0)

# Perform calculations
G = V * rho  # Calculated mass of the block
beta_rad = beta * (3.14159265 / 180)  # Convert to radians
alpha_rad = alpha * (3.14159265 / 180)  # Convert to radians
phi_rad = phi * (3.14159265 / 180)  # Convert to radians

# Calculate the safety factor F
numerator = c * A + (G * math.cos(beta_rad) - U + T * math.sin(alpha_rad)) * math.tan(phi_rad)
denominator = G * math.sin(beta_rad) - T * math.cos(alpha_rad)

if denominator != 0:
    F = numerator / denominator
else:
    F = 'Udefinert (deling på 0)'

st.write('Sikkerhetsfaktor er: ', F)
