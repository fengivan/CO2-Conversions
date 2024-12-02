import streamlit as st
import pandas as pd
import sys
import streamlit as st
from CoolProp.CoolProp import PropsSI

st.set_page_config(page_title="CO2 Properties", layout="wide")

st.divider()
st.header("Pure CO2 Unit Converter")
data = {
    "Temp Base (F)": [70, 70, 60, 60],
    "Pressure Base (psia)": [14.65, 14.73, 14.65, 14.73],
    "CO2 Density (g/L)": [1.8265, 1.8365, 1.8623, 1.8725],
    "MT/MMcf": [51.7210005, 52.0041705, 52.7347491, 53.0235825],
}
df = pd.DataFrame(data)
mixture = "CO2[1]"
df["CO2 Density (g/L)"] = df.apply(lambda row: PropsSI('D', 'T', (row["Temp Base (F)"]+459.67)/1.8, 'P',row["Pressure Base (psia)"]*6894.76, mixture), axis=1)
df['MT/MMcf']= df["CO2 Density (g/L)"] *.0283168466*1000



pressure_col1, pressure_col2, _ = st.columns([1, 1, 4]) 
with pressure_col1:
    pressure_base = st.selectbox("Select Gas Pressure Base:", ["14.65 psi, 60F (RRC)", "14.65 psi, 70F", "14.73 psi, 60F", "14.73 psi, 70F"], index=0)


parts = pressure_base.split(", ") 
pressure = float(parts[0].split()[0]) 
temp = float(parts[1].split("F")[0]) 

factor = df[(df['Temp Base (F)'] == temp) & (df['Pressure Base (psia)'] == pressure)]['MT/MMcf'].iloc[0]


col1, col2, _ = st.columns([1, 1, 6]) 

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
    st.write("Selected Input:", co2_value, unit)

if unit =='Metric Tons/year':
    summary_data = {
    'Units                        ': ['12-Year Total Metric Tons', 'Metric Tons/year', 'MCFD', 'bbls/day (1,000 psig, 80F)'],
    'Value                        ': [
        round(co2_value*12,1),
        co2_value, 
        round(co2_value/365/factor*1000,1), 
        round(co2_value*.0242665,1) 
    ]
    }
elif unit =='MCFD':
    summary_data = {
    'Units                       ': ['12-Year Total Metric Tons', 'Metric Tons/year', 'MCFD', 'bbls/day (1,000 psig, 80F)'],
    'Value                       ': [
        round(co2_value*365*factor/1000*12,1),
        round(co2_value*365*factor/1000,1),  
        co2_value,
        round(co2_value*365*factor/1000*.0242665,1) 
    ]
    }

summary_df = pd.DataFrame(summary_data)
st.dataframe (summary_df)

st.divider()########################################################################################################################################################################
st.header("Compositional Properties")


col1, col2, col3, col4, col5, col6= st.columns(6)

with col1:
    st.header("Temperature and Pressure")
    temperature = st.number_input("Temperature (°F)", min_value=32.0, max_value=1000.0, value=80.0)
    pressure = st.number_input("Pressure (psia)", min_value=1.0, max_value=20000.0, value=1000.0)


with col2:
    st.header("Gas Composition (Mole Fraction)")
    co2_percent = st.number_input("CO2 (%)", min_value=0.0, max_value=100.0, value=100.0)/100
    h2s_percent = st.number_input("H2S (%)", min_value=0.0, max_value=100.0, value=0.0)/100
    ch4_percent = st.number_input("CH4 (%)", min_value=0.0, max_value=100.0, value=0.0)/100
    c2h6_percent = st.number_input("C2H6 (%)", min_value=0.0, max_value=100.0, value=0.0)/100

total_gas_percent = co2_percent + h2s_percent + ch4_percent+c2h6_percent




mixture = "CO2[1]"
mixture = "Methane["+str(ch4_percent)+"]&CO2["+str(co2_percent)+"]&H2S["+str(h2s_percent)+"]&ethane["+str(c2h6_percent)+"]"




if total_gas_percent == 1:
    st.success("Inputs look good!")
    co2_percent=co2_percent/total_gas_percent
    h2s_percent=h2s_percent/total_gas_percent
    ch4_percent=ch4_percent/total_gas_percent
    c2h6_percent=c2h6_percent/total_gas_percent
    total_gas_percent = co2_percent + h2s_percent + ch4_percent+c2h6_percent
    data = {
        'Parameter': ['Temperature', 'Pressure', 'CO2', 'H2S', 'CH4', 'C2H6'],
        'Value': [temperature, pressure, co2_percent, h2s_percent, ch4_percent, c2h6_percent],
        'Unit': ['°F', 'psia', 'mole fraction', 'mole fraction', 'mole fraction', 'mole fraction']
    }

    # Convert dictionary to DataFrame
    df2 = pd.DataFrame(data)

    # Display the DataFrame using Streamlit
    st.write("### Summary of Inputs:")
    st.dataframe(df2)

    st.write("Density (g/L): "+str(PropsSI('D', 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))
    st.write("Viscosity (cP): "+str(1000*PropsSI("VISCOSITY", 'T', (temperature+459.67)/1.8, 'P',pressure*6894.76, mixture)))

else:

    st.error("Total gas percentage not 100%. Please adjust your inputs.")
    st.write(total_gas_percent*100)
st.divider()########################################################################################################################################################################
st.header('References')
st.write("RRC Gas Production Reporting: https://www.rrc.texas.gov/media/mxcpw5vn/form-pr-instructions-01-25-2022.pdf")
st.dataframe(df)


st.markdown("""
### 
For more information on the thermophysical property evaluation and the CoolProp library, please refer to the following publication:

Bell, I. H., Wronski, J., Quoilin, S., & Lemort, V. (2014). *Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and the Open-Source Thermophysical Property Library CoolProp*. *Industrial & Engineering Chemistry Research*, 53(6), 2498–2508. [https://doi.org/10.1021/ie4033999](https://doi.org/10.1021/ie4033999)
""")

st.write("http://www.coolprop.org/index.html")