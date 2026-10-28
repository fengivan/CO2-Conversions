import folium
from folium.plugins import MeasureControl
from folium import CircleMarker, PolyLine
from io import StringIO
import math
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re
from scipy.optimize import curve_fit
import streamlit as st
from streamlit.components.v1 import html
from streamlit_folium import st_folium
import sys

st.set_page_config(layout="wide")

def clean_string(s):
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)

def format_api(api):
    api = str(api).zfill(14)  # Ensure it's 14 digits
    return f"{api[:2]}-{api[2:5]}-{api[5:10]}-{api[10:12]}-{api[12:]}"

def arps(t, qi, db, n, de=.06): # returns 
    t=np.arange(len(t)+1)
    Ai = 1 / n * ((1 - db) ** (-1 * n) - 1) / 12
    Df = 1 - (1 + n * (-math.log(1 - de))) ** (-1 / n)
    Af = 1 / n * ((1 - Df) ** (-1 * n) - 1) / 12
    tc = round((Ai - Af) / (n * Ai * Af))
    finalrate=qi/(1+n*(tc)*Ai)**(1/n)
    Ai2 = -math.log(1-de)
    finalrate2=finalrate*math.exp(-1*Ai2*(600-tc)/12)
    
    results = []
    results2 = []
    for time in t:
        
        endmonthrate = finalrate*math.exp(-1*Ai2*(time-tc)/12)
        Cum2 = (finalrate2-endmonthrate)/(Ai2/12)
        Qf = qi / (1 + n * Ai * time) ** (1 / n)
        Np = qi ** n * (qi ** (1 - n) - Qf ** (1 - n)) / ((1 - n) * Ai)
        q = qi * (1 + n * Ai * time) ** (-1 / n)  # rates
        Cum = (qi ** n) * (qi ** (1 - n) - q ** (1 - n)) / ((1 - n) * Ai)

        results.append(Cum)
        results2.append(Cum2)
        
    results = [results[i+1] - results[i] for i in range(len(results)-1)]
    results2= [results2[i+1] - results2[i] for i in range(len(results2)-1)]
    return np.array(results[:tc] + results2[tc:])#, tc

def fit(dailyRates, weights, initial_guess, bounds, de, ignore = 1):

        cleaned = dailyRates.dropna()
        x = np.arange(len(cleaned))[ignore:]         # skip first point
        y = cleaned.values[ignore:]                  # skip first point
        weights = weights[ignore:]

      #  initial_guess = [np.max(y), .66, .9]
      #  bounds = ([.001, .3, .75], [np.max(y)*2.5, .99, 1.2])

        # Fit the data using curve_fit
        params, covariance = curve_fit(arps,x, y,bounds = bounds, sigma = 1/weights, p0=initial_guess)

        # Extract the fitted parameters
        qi_fit, db_fit, n_fit = params
        #st.write(f"Avg Gas Fitted Parameters: qi = {qi_fit}, db = {db_fit}, n = {n_fit}")

        # Generate the fitted production data
        production_fitted = np.array(arps(x, *params, de = de))
        return production_fitted, qi_fit, db_fit, n_fit
    
        historical = gasD[i].loc[gasD[i].first_valid_index() : gasD[i].last_valid_index()]



        gas_production_fitted, gas_qi_fit, gas_db_fit, gas_n_fit = fit(historical, True)



        gas_50_year = arps(np.zeros(599), gas_qi_fit,gas_db_fit, gas_n_fit)
        st.write("Gas qi fit:", gas_qi_fit)
        st.write("Gas db fit:", gas_db_fit)
        st.write("Gas n fit:", gas_n_fit)
        st.write("EUR:", gas_50_year.sum()*365/12/1000000)
        start_date = historical.index[1]

        # generate a new datetime index for the length of the fit
        fit_index = pd.date_range(start=start_date, periods=len(gas_50_year), freq='MS')

        # create a DataFrame to combine
        temp = pd.DataFrame({
            'Historical Gas (Mcf/d)': historical,
            'Forecasted Gas (Mcf/d)': pd.Series(gas_50_year, index=fit_index)
        })



pasted_data = st.text_area(
    "Paste tab-delimited Monthly data here:",
    height=200,
    placeholder="Month\t Prod\n1\t100\n2\t50"
)


try:
    # Use StringIO to treat pasted text as a file
    df = pd.read_csv(StringIO(pasted_data), sep="\t")
    st.success("Data loaded successfully!")
    st.dataframe(df,height=150, width=400)
    df.iloc[:, 1]=df.iloc[:, 1]*12/365
    col1, divider1, col2, divider2, col3 = st.columns([10,1,10,1,10])

    with col1:
        use_log = st.checkbox("Use log scale for left Y-axis", value=False)

    with divider1:
        st.markdown("<div style='border-left:1px solid #ddd;height:50px;margin:0 10px'></div>", unsafe_allow_html=True)

    with col2:
        ignore_months = st.number_input(
            "Ignore first X months",
            min_value=0,
            max_value=3,
            value=1,
            step=1,
        )

    with divider2:
        st.markdown("<div style='border-left:1px solid #ddd;height:50px;margin:0 10px'></div>", unsafe_allow_html=True)

    with col3:
        apply_weight = st.checkbox("Prioritize recent data", value=False)
        weight_degree = st.slider(
            "Weight degree",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=0.1,
            disabled=not apply_weight
        )


    st.markdown("### Curve Fit Parameters and Bounds")

    with st.expander("Adjust Fit Parameters and Bounds"):

        col1, col2, col3 = st.columns(3)

        with col1:
            qi = st.number_input("Initial guess qi", value=float(df.iloc[:,1].max()))
            qi_min = st.number_input("Min qi", value=0.0)
            qi_max = st.number_input("Max qi", value=df.iloc[:,1].max()*2)

        with col2:
            di = st.number_input("Initial guess di", value=float(.66))
            di_min = st.number_input("Min di", value=0.3)
            di_max = st.number_input("Max di", value=0.99)

        with col3:
            n = st.number_input("Initial guess n", value=float(.9))
            n_min = st.number_input("Min n", value=.75)
            n_max = st.number_input("Max n", value=1.2)

        de = st.number_input("Default de (not fitted)", value=.06)

    # Collect initial guesses and bounds
    initial_guess = [qi, di, n]
    bounds = ([qi_min, di_min, n_min], [qi_max, di_max, n_max])





    fit, *params = fit(df.iloc[:,1],np.exp(np.linspace(0, weight_degree, len(df.iloc[:,1]))), initial_guess=initial_guess, bounds = bounds, de = de)
    


    fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                'Rate','Cum'
            ],
            shared_xaxes=True
        )
    fig.add_trace(go.Scatter(
        x=df.iloc[:, 0],
        y=df.iloc[:, 1],
        mode='markers',
        name='Input Monthly Prod' 
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.iloc[:, 0],
        y=np.cumsum(df.iloc[:, 1]),
        mode='markers',
        name='Input Cum' 
    ), row=1, col=2)



    fig.add_trace(go.Scatter(
        x=np.arange(2,602),
        y=arps(np.zeros(600), *params),
        mode='lines',
        name='Autofit Monthly Rate' 
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=np.arange(2,602),
        y=np.cumsum(arps(np.zeros(600), *params))+df.iloc[:,1][0:ignore_months].sum(),
        mode='lines',
        name='Autofit Monthly Cum' 
    ), row=1, col=2)

    fig.update_yaxes(type="log" if use_log else "linear", row=1, col=1)
    fig.update_xaxes(range=[0, df.iloc[:, 0].max()+24], row = 1, col =1)
    fig.update_xaxes(range=[0, df.iloc[:, 0].max()+24], row = 1, col =2)
    # fig.update_yaxes(range=[min(df.iloc[:, 1].min(1)), max(df.iloc[:, 1].max(*1.5))], row =1, col = 1)




    add_manual_curve = st.checkbox("Add manual input curve")





    if add_manual_curve:
        st.markdown("### Manual Input Parameters")

        col1, col2, col3 = st.columns(3)

        with col1:
            qi_manual = st.number_input("qi", value=params[0])
        with col2:
            di_manual = st.number_input("di", value=params[1])
        with col3:
            n_manual = st.number_input("n", value=params[2])

        
        y_manual = arps(np.zeros(600), qi_manual, di_manual, n_manual)

        fig.add_trace(go.Scatter(
            x=np.arange(2,602),
            y=y_manual,
            mode='lines',
            name='Manual Curve',
            line=dict(dash='dash', color='grey')
        )            ,    row = 1, col = 1)
        fig.add_trace(go.Scatter(
            x=np.arange(2,602),
            y=np.cumsum(y_manual)+df.iloc[:,1][0:ignore_months].sum(),
            mode='lines',
            name='Manual Curve',
            line=dict(dash='dash', color='grey')
        )           ,     row = 1, col = 2)

    st.divider()
    col1, col2, col3, col4= st.columns(4)

    with col1:
        st.metric("qi", f"{params[0]:.3f}")

    with col2:
        st.metric("di", f"{params[1]:.3f}")

    with col3:
        st.metric("b", f"{params[2]:.3f}")
    with col4:
        st.metric("de", f"{de:.3f}")


    st.plotly_chart(fig)


    st.write("EUR: "+ str(np.round(np.sum(arps(np.zeros(600), *params))*365/12)))




    temp = pd.DataFrame({
        'Month': np.arange(2,602),
        'Forecast': arps(np.zeros(600), *params)*365/12
    })

    st.dataframe(temp)











except Exception as e:
    st.error(f"Error reading data: {e}")












st.divider()