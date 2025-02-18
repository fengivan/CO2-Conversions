import streamlit as st
import pandas as pd
import sys
import streamlit as st
from CoolProp.CoolProp import PropsSI
import math
st.set_page_config(page_title="CO2 Properties", layout="centered")

st.divider()
st.header("Pure CO2 Unit Converter")
data = {
    "Temp Base (F)": [70, 70,70,70, 60, 60,60,60,59],
    "Pressure Base (psia)": [14.65, 14.696,14.7,14.73, 14.65, 14.696,14.7,14.73,14.7],
    #"CO2 Density (g/L)": [1.8265, 1.8365, 1.8623, 1.8725],
    #"MT/MMcf": [51.7210005, 52.0041705, 52.7347491, 53.0235825],
}
df = pd.DataFrame(data)
mixture = "CO2[1]"
df["CO2 Density (g/L)"] = df.apply(lambda row: PropsSI('D', 'T', (row["Temp Base (F)"]+459.67)/1.8, 'P',row["Pressure Base (psia)"]*6894.76, mixture), axis=1)
df['MT/MMcf']= df["CO2 Density (g/L)"] *.0283168466*1000




pressure_base = st.selectbox("Select Gas Pressure Base:", ["14.65 psi, 60F (RRC)", "14.65 psi, 70F", "14.696 psi, 60F", "14.696 psi, 70F", "14.73 psi, 60F", "14.73 psi, 70F", "14.7 psi, 59F (new)"], index=0)


parts = pressure_base.split(", ") 
pressure = float(parts[0].split()[0]) 
temp = float(parts[1].split("F")[0]) 

factor = df[(df['Temp Base (F)'] == temp) & (df['Pressure Base (psia)'] == pressure)]['MT/MMcf'].iloc[0]


col1, col2 = st.columns([1, 1]) 

with col1:
    co2_value_input = st.text_input("Input:", value="100000") 

    try:
        co2_value = float(co2_value_input)
    except ValueError:
        co2_value = None
        st.error("Please enter a valid whole number.")

with col2:
    unit = st.selectbox("Unit:", ["Metric Tons/year", "MCFD"])

# Display user input if valid
if co2_value is not None:
    st.write("Selected pressure base:", pressure_base)
    st.write("Conversion Factor:", factor, "MT/MMCF")
    st.write("Selected Input:", co2_value, unit)
    

if unit =='Metric Tons/year':
    summary_data = {
    'Units                        ': ['12-Year Total Metric Tons', 'Metric Tons/year', 'MCFD', 'bbls/day (1,400 psig, 80F)'],
    'Value                        ': [
        round(co2_value*12,1),
        co2_value, 
        round(co2_value/365/factor*1000,1), 
        round(co2_value*.0215761,1) 
    ]
    }
elif unit =='MCFD':
    summary_data = {
    'Units                       ': ['12-Year Total Metric Tons', 'Metric Tons/year', 'MCFD', 'bbls/day (1,400 psig, 80F)'],
    'Value                       ': [
        round(co2_value*365*factor/1000*12,1),
        round(co2_value*365*factor/1000,1),  
        co2_value,
        round(co2_value*365*factor/1000*.0215761,1) 
    ]
    }

summary_df = pd.DataFrame(summary_data)
st.dataframe (summary_df)

st.divider()########################################################################################################################################################################
st.header("Compositional Properties")




st.write("**Temperature and Pressure**")
temperature = st.number_input("Temperature (°F)", min_value=32.0, max_value=1000.0, value=80.0)
pressure = st.number_input("Pressure (psia)", min_value=1.0, max_value=20000.0, value=1400.0)
col2, col3= st.columns(2)


with col2:
    st.write("**Gas Composition (Mole Fraction)**")
    co2 = st.number_input("CO2", min_value=0.0, max_value=100000.0, value=100.0)
    h2s = st.number_input("H2S", min_value=0.0, max_value=100000.0, value=0.0)
    ch4 = st.number_input("CH4", min_value=0.0, max_value=100000.0, value=0.0)
    c2h6 = st.number_input("C2H6", min_value=0.0, max_value=100000.0, value=0.0)
    n2 = st.number_input("N2", min_value=0.0, max_value=100000.0, value=0.0)

    total_gas= co2+ h2s + ch4 + c2h6+n2
    co2_percent=co2/total_gas
    h2s_percent=h2s/total_gas
    ch4_percent=ch4/total_gas
    c2h6_percent=c2h6/total_gas
    n2_percent = n2/total_gas

mixture = "CO2[1]"
mixture = "Methane["+str(ch4_percent)+"]&CO2["+str(co2_percent)+"]&H2S["+str(h2s_percent)+"]&ethane["+str(c2h6_percent)+"]&N2["+str(n2_percent)+"]"



total_gas_percent = co2_percent + h2s_percent + ch4_percent+c2h6_percent+n2_percent
data = {
    'Parameter': ['Temperature', 'Pressure', 'CO2', 'H2S', 'CH4', 'C2H6', 'N2'],
    'Value': [temperature, pressure, co2_percent, h2s_percent, ch4_percent, c2h6_percent, n2_percent],
    'Unit': ['°F', 'psia', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction']
}

# Convert dictionary to DataFrame
df2 = pd.DataFrame(data)

# Display the DataFrame using Streamlit
with col3:
    st.write("**Summary of Inputs:**")
    st.dataframe(df2)

st.header("Results")
#st.write("Phase: "+str(PropsSI("Phase", 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))

st.write("Density (g/L): "+str(PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))
st.write("Density (Metric Ton/BBL): "+str(PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)*1.59*10**-4))
st.write("Density (lb/gallon): "+str(PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)*.008345))




st.write("Viscosity (cP): "+str(1000*PropsSI("VISCOSITY", 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))


fvf=PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)/PropsSI('D', 'T', (60+459.67)/1.8, 'P',14.65*6894.76, mixture)
st.write("Gas FVF (v/v): " +str(fvf))

den = PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, 'CO2[1]')


st.write('Eq CO2: (Metric Ton/BCF):' +str(den/fvf/.0000353))


air = PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, 'CO2[1]')

st.write(den)

st.divider()########################################################################################################################################################################





st.divider()########################################################################################################################################################################
st.header('References')
st.write("RRC Gas Production Reporting Instructions: https://www.rrc.texas.gov/media/mxcpw5vn/form-pr-instructions-01-25-2022.pdf")
st.dataframe(df)


st.markdown("""
### 
For more information on the thermophysical property evaluation and the CoolProp library, please refer to the following publication:

Bell, I. H., Wronski, J., Quoilin, S., & Lemort, V. (2014). *Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and the Open-Source Thermophysical Property Library CoolProp*. *Industrial & Engineering Chemistry Research*, 53(6), 2498–2508. [https://doi.org/10.1021/ie4033999](https://doi.org/10.1021/ie4033999)
""")

st.write("http://www.coolprop.org/index.html")
st.write(" ")
st.write("NIST Carbon Dioxide Properties: https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389")