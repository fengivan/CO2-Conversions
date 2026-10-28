import streamlit as st
import pandas as pd
import sys
import streamlit as st
from CoolProp.CoolProp import PropsSI
import math
import numpy as np
st.set_page_config(page_title="CO2 Properties", layout="centered")


st.header("Tubing Friction")

length = st.number_input("Length (ft)", min_value=1, max_value=100000, value=14400)
Tsurf = st.number_input("Stream Entering Temperature", min_value = 60, max_value= 400, value = 100)
Tbot = st.number_input("Stream Exit Temperature", min_value = 60, max_value= 400, value = 120)
pressure = st.number_input("BHP", min_value = 10, max_value= 20000, value = 12000)
segments = st.number_input("Segments", min_value = 1, max_value= 200, value = 20)

col2, col3= st.columns(2)
with col2:
    st.write("**Gas Composition (Mole Fraction)**")
    co2 = st.number_input("CO2", min_value=0.0, max_value=100000.0, value=100.0)
    h2s = st.number_input("H2S", min_value=0.0, max_value=100000.0, value=0.0)
    ch4 = st.number_input("CH4", min_value=0.0, max_value=100000.0, value=0.0)
    c2h6 = st.number_input("C2H6", min_value=0.0, max_value=100000.0, value=0.0)
    c3h8 = st.number_input("C3H8", min_value=0.0, max_value=100000.0, value=0.0)
    n2 = st.number_input("N2", min_value=0.0, max_value=100000.0, value=0.0)
    

    total_gas= co2+ h2s + ch4 + c2h6+ c3h8+ n2 
    co2_percent=co2/total_gas
    h2s_percent=h2s/total_gas
    ch4_percent=ch4/total_gas
    c2h6_percent=c2h6/total_gas
    c3h8_percent=c3h8/total_gas
    n2_percent = n2/total_gas


mixture = "Methane["+str(ch4_percent)+"]&CO2["+str(co2_percent)+"]&H2S["+str(h2s_percent)+"]&ethane["+str(c2h6_percent)+"]&propane["+str(c3h8_percent)+"]&N2["+str(n2_percent)+"]"



total_gas_percent = co2_percent + h2s_percent + ch4_percent+c2h6_percent+n2_percent + c3h8_percent
data = {
    'Parameter': ['Length', 'Segments', 'Entry Temp', 'Exit Temp', 'BHP', 'CO2', 'H2S', 'CH4', 'C2H6', 'C3H8', 'N2'],
    'Value': [length, segments, Tsurf, Tbot, pressure, co2_percent, h2s_percent, ch4_percent, c2h6_percent, c3h8_percent, n2_percent],
    'Unit': ['ft', ' ', '°F', '°F', 'psia', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction']
}



# Convert dictionary to DataFrame
df2 = pd.DataFrame(data)

# Display the DataFrame using Streamlit
with col3:
    st.write("**Summary of Inputs:**")
    st.dataframe(df2)



st.header("Results")





# Constants
g = 9.80665  # gravity in m/s²
psi_to_Pa = 6894.76
psia_offset = 14.6959

# Your setup
pressures = np.zeros(segments)  # psig
pressures[-1] = pressure  # bottomhole pressure in psig
segmentL = length / segments  # ft
segmentL_m = segmentL * 0.3048  # convert to meters
temps = np.linspace(Tsurf, Tbot, segments)  # °F
densities = np.zeros(segments)
velocities = np.zeros(segments)
hydrostatic = np.zeros(segments)
depths = np.linspace(0, length, segments)

# Bottom segment density (initial)
densities[-1] = PropsSI('D', 'T', (temps[-1]+459.67)/1.8, 'P', (pressures[-1]+psia_offset)*psi_to_Pa, mixture)



for i in range(segments-2, -1, -1):
    # Estimate pressure at next depth (initial guess = same as below)
    p_next = pressures[i+1]
    T = temps[i]
    
    # Convert T (°F) to K and pressure (psig) to Pa
    T_K = (T + 459.67) / 1.8
    P_Pa = (p_next + psia_offset) * psi_to_Pa
    
    # Get density at this segment
    rho = PropsSI('D', 'T', T_K, 'P', P_Pa, mixture)  # kg/m³
    densities[i] = rho

    # Hydrostatic pressure change: dP = rho * g * dh
    dP = rho * g * segmentL_m  # in Pascals
    dP_psi = dP / psi_to_Pa

    # Pressure at this segment
    pressures[i] = pressures[i+1] - dP_psi
    hydrostatic[i] = dP_psi


st.write("Done")

data = np.column_stack((depths, temps, pressures, densities))
df = pd.DataFrame(data, columns=['Depth(ft)', 'Temp(F)', 'Pressure(psig)' ,'Density(lb/gal)'])
st.dataframe(df, use_container_width=True, height=len(df) * 35+35)



st.divider()########################################################################################################################################################################







#st.write("Phase: "+str(PropsSI("Phase", 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))

st.write("Density (g/L): "+str(PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, mixture)))
st.write("Density (Metric Ton/BBL): "+str(PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, mixture)*1.59*10**-4))
st.write("Density (lb/gallon): "+str(PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, mixture)*.008345))




st.write("Viscosity (cP): "+str(1000*PropsSI("VISCOSITY", 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, mixture)))


fvf=PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, mixture)/PropsSI('D', 'T', (60+459.67)/1.8, 'P',14.65*6894.76, mixture)
st.write("Gas FVF (v/v): " +str(fvf))

den = PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, 'CO2[1]')




air = PropsSI('D', 'T', (Tsurf+459.67)/1.8, 'P',pressure*6894.76, 'CO2[1]')

st.write(den)

st.divider()########################################################################################################################################################################





st.divider()########################################################################################################################################################################
st.header('References')
st.write("RRC Gas Production Reporting Instructions: https://www.rrc.texas.gov/media/mxcpw5vn/form-pr-instructions-01-25-2022.pdf")

st.markdown("""
### 
For more information on the thermophysical property evaluation and the CoolProp library, please refer to the following publication:

Bell, I. H., Wronski, J., Quoilin, S., & Lemort, V. (2014). *Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and the Open-Source Thermophysical Property Library CoolProp*. *Industrial & Engineering Chemistry Research*, 53(6), 2498–2508. [https://doi.org/10.1021/ie4033999](https://doi.org/10.1021/ie4033999)
""")

st.write("http://www.coolprop.org/index.html")
st.write(" ")
st.write("NIST Carbon Dioxide Properties: https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389")