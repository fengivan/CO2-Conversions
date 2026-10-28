import streamlit as st
import pandas as pd
import sys
import streamlit as st
import math
import numpy as np
import re
from folium.plugins import MeasureControl
import folium
import plotly.graph_objs as go
from folium import CircleMarker, PolyLine
from streamlit_folium import st_folium
from scipy.optimize import curve_fit
from plotly.subplots import make_subplots
from streamlit.components.v1 import html
st.set_page_config(layout="wide")
def clean_string(s):
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)
def format_api(api):
    api = str(api).zfill(14)  # Ensure it's 14 digits
    return f"{api[:2]}-{api[2:5]}-{api[5:10]}-{api[10:12]}-{api[12:]}"
def arps(t, qi, db, n, de=.05):
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

st.title("Upload Well Data")

# Upload Well Headers
well_headers_file = st.file_uploader("Upload Well Headers CSV", type=["csv"], key="well_headers")

# Upload Prod
prod_file = st.file_uploader("Upload Production CSV", type=["csv"], key="prod")

# Check if both files are uploaded
if True:# well_headers_file is not None and prod_file is not None:
    # Read the CSV files into DataFrames
    #wells = pd.read_csv(well_headers_file)
    #prod = pd.read_csv(prod_file).rename(columns={'API/UWI': 'API14'})

    wells = pd.read_csv("StarTex System Edwards Producers Well Headers.CSV")
    prod= pd.read_csv("StarTex System Edwards Producers Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    
    

    

    st.success("Both files uploaded successfully!")

    wells['Spud Date'] = pd.to_datetime(wells['Spud Date'], errors='coerce')
    wells['Completion Date'] = pd.to_datetime(wells['Completion Date'], errors='coerce')

    # Display initial sizes
    st.write("### Initial Data")
    st.write(f"Initial Wells Count: {str(len(wells))}")
    st.write(f"Initial Unique Production APIs: {str(len(prod['API14'].unique()))}")

    # Filter by API14 match
    prod['API14'] = prod['API14'].astype(str).str.zfill(14)
    wells['API14'] = wells['API14'].astype(str).str.zfill(14)
    prod = prod[prod['API14'].isin(wells['API14'])]
    wells = wells[wells['API14'].isin(prod['API14'])]


    # Clean and merge names
    wells['Well Name'] = (wells['Well Name'].astype(str) + " " + wells['Well Number'].astype(str)).apply(clean_string)
    prod['Well Name'] = (prod['Well Name'].astype(str) + " " + prod['Well Number'].astype(str)).apply(clean_string)
    prod['Monthly Production Date'] = pd.to_datetime(prod['Monthly Production Date'], errors='coerce')

    # Display filtered sizes
    st.write("### After Filtering")
    st.write(f"Filtered Wells Count: {len(wells)}")
    st.write(f"Filtered Unique Production APIs: {len(prod['API14'].unique())}")

    # Merge dataframes
    merged = pd.merge(
        wells[[col for col in wells.columns if col == 'API14' or col not in prod.columns]],
        prod,
        on='API14'
    )

##Plot Wells On a Map
        # Required columns
    surface_lat_col = 'Surface Hole Latitude (WGS84)'
    surface_lon_col = 'Surface Hole Longitude (WGS84)'
    bottom_lat_col = 'Bottom Hole Latitude (WGS84)'
    bottom_lon_col = 'Bottom Hole Longitude (WGS84)'
    name_col = 'Well Name'
    operator_col = 'Operator Company Name'

    # Check required columns
    required_cols = [surface_lat_col, surface_lon_col, name_col, operator_col]
    if not all(col in wells.columns for col in required_cols):
        st.error("Missing required columns in the uploaded file.")
    else:
        # Remove rows without surface coordinates
        wells['API14_formatted'] = wells['API14'].apply(format_api)

        # Map center
        avg_lat = wells[surface_lat_col].mean()
        avg_lon = wells[surface_lon_col].mean()
        st.dataframe(wells)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)

        for _, row in wells.iterrows():
            lateral_length = f"{int(row['DI Lateral Length']):,} ft" if pd.notna(row['DI Lateral Length']) else "N/A"
            cum_oil = f"{int(row['Cum Oil']):,}" if pd.notna(row['Cum Oil']) else "N/A"
            eur_oil = f"{int(row['EUR Oil (BE)']):,}" if pd.notna(row['EUR Oil (BE)']) else "N/A"
            cum_gas = f"{int(row['Cum Gas']):,}" if pd.notna(row['Cum Gas']) else "N/A"
            eur_gas = f"{int(row['EUR Gas (BE)']):,}" if pd.notna(row['EUR Gas (BE)']) else "N/A"

            tooltip = f"""
            <table style="font-size: 12px; border-spacing: 6px;">
            <tr><td><b>Operator:</b></td><td>{row['Operator Company Name']}</td></tr>
            <tr><td><b>Well Name:</b></td><td>{row['Well Name']}</td></tr>
            <tr><td><b>API14:</b></td><td>{row['API14_formatted']}</td></tr>
            <tr><td><b>Lateral Length:</b></td><td>{lateral_length}</td></tr>
            <tr><td><b>Oil (Cum/EUR):</b></td><td>{cum_oil} / {eur_oil}</td></tr>
            <tr><td><b>Gas (Cum/EUR):</b></td><td>{cum_gas} / {eur_gas}</td></tr>
            </table>
            """



            color_map = {
                'OIL': 'green',
                'GAS': 'red',
                'OIL & GAS' :'green'
            }
            color = color_map.get(row['Production Type'], 'black')

            # Draw circle at surface location
            CircleMarker(
                location=[row[surface_lat_col], row[surface_lon_col]],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.5,
                tooltip=tooltip
            ).add_to(m)

            # If bottom hole exists, draw a line
            if pd.notnull(row.get(bottom_lat_col)) and pd.notnull(row.get(bottom_lon_col)):
                PolyLine(
                    locations=[
                        [row[surface_lat_col], row[surface_lon_col]],
                        [row[bottom_lat_col], row[bottom_lon_col]]
                    ],
                    color=color,
                    weight=2,
                    tooltip=tooltip
                ).add_to(m)
        m.add_child(MeasureControl(primary_length_unit='feet', primary_area_unit='acres'))

        # Display map in Streamlit
        st.write("### Well Surface and Trajectory Map")
        #st_folium(m, width=774, height=500)


        m_html = m._repr_html_()

        # Embed the map using a controlled height iframe
        html(m_html, height=500)  # Adjust height as needed
    st.markdown("---")




#total production over time
#########################################################################################################################################################################################################

    st.markdown("---")





    # Pivot tables
    gas = prod.pivot_table(index='Monthly Production Date', columns='Well Name', values='Monthly Gas').sort_index()
    oil = prod.pivot_table(index='Monthly Production Date', columns='Well Name', values='Monthly Oil').sort_index()

    # Sum across wells
    total_gas = gas.sum(axis=1)
    total_oil = oil.sum(axis=1)
    producing_wells = ((gas.fillna(0) > 0) | (oil.fillna(0) > 0)).sum(axis=1)


    # Create subplots (2 rows, shared x-axis)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,
        row_heights=[0.8, 0.2],  # Top row taller than bottom
        specs=[[{"secondary_y": True}], [{}]],
        subplot_titles=['Total Oil and Gas Production Over Time', 'Number of Producing Wells']
    )

    # --- Row 1: Production with dual y-axes ---
    # Oil trace (left y-axis)
    fig.add_trace(go.Scatter(
        x=total_oil.index,
        y=total_oil,
        mode='lines',
        name='Oil',
        line=dict(color='green')
    ), row=1, col=1, secondary_y=False)

    # Gas trace (right y-axis)
    fig.add_trace(go.Scatter(
        x=total_gas.index,
        y=total_gas,
        mode='lines',
        name='Gas',
        line=dict(color='red')
    ), row=1, col=1, secondary_y=True)

    # --- Row 2: Producing Wells Bar Chart ---
    fig.add_trace(go.Bar(
        x=producing_wells.index,
        y=producing_wells,
        name='Producing Wells',
        marker_color='grey'
    ), row=2, col=1)

    # Layout updates
    fig.update_yaxes(title_text="Oil (BBL/Month)", color='green', row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Gas (MCF/Month)", color='red', row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="# of Wells", row=2, col=1)

    fig.update_xaxes(title_text="Production Date", row=2, col=1)

    fig.update_layout(
        height=700,
        width=1000,
        showlegend=False,
        title_text=""
    )
    vertical_spacing=0.15  # Increase from 0.08


    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)




#PDP forecasting
#########################################################################################################################################################################################################


    st.markdown("---")

    st.header("Gas Forecasts")

    #common issue is that production data can skip some months. 


    gasD = prod.pivot_table(index='Monthly Production Date', columns='Well Name', values='Avg Gas').sort_index()
    st.dataframe(gasD.head(10))

    def fit(dailyRates, weight = False):

        cleaned = dailyRates.dropna()
        x = np.arange(len(cleaned))[1:]         # skip first point
        y = cleaned.values[1:]                  # skip first point
        weights = np.ones(len(x))
        
        if weight:
            x = x[-24:]
            y = y[-24:]
            weights = weights[-24:]
            #weights =  np.exp(np.linspace(0, 3, len(x)))
               
        sliced_off = len(cleaned) - len(x)


        initial_guess = [np.max(y), .8, .8]
        bounds = ([.001, .3, .6], [np.max(y)*2.5, .99, 1.2])

        # Fit the data using curve_fit
        params, covariance = curve_fit(arps,x, y,bounds = bounds, sigma = 1/weights, p0=initial_guess)

        # Extract the fitted parameters
        qi_fit, db_fit, n_fit = params
        #st.write(f"Avg Gas Fitted Parameters: qi = {qi_fit}, db = {db_fit}, n = {n_fit}")

        # Generate the fitted production data
        production_fitted = np.array(arps(x, *params))
        if weight:
            return np.concatenate([np.full(sliced_off, 0), production_fitted]), qi_fit, db_fit, n_fit

        return production_fitted, qi_fit, db_fit, n_fit
    

    

    forecasts = None
    historicals=None
    for i in gasD.columns:

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

  



        col1, col2, col3 = st.columns([1, 4, 1])  # center column is wider
        #with col2:
         #   st.dataframe(temp)
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Daily Gas Production", "Cumulative Gas Production"]
        )

        # --- Left subplot: daily rates ---
        fig.add_trace(go.Scatter(
            x=temp.index[0:300],
            y=temp['Historical Gas (Mcf/d)'][0:300],
            name='Historical Gas',
            line=dict(color='red')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=temp.index[1:300],
            y=temp['Forecasted Gas (Mcf/d)'][1:300],
            name='Forecasted Gas',
            line=dict(color='black', dash='dash')
        ), row=1, col=1)

        # --- Right subplot: cumulative sums ---
        fig.add_trace(go.Scatter(
            x=temp.index[0:300],
            y=temp['Historical Gas (Mcf/d)'].cumsum()[0:300]*365/12,
            name='Cumulative Historical Gas',
            line=dict(color='red')
        ), row=1, col=2)

        fig.add_trace(go.Scatter(
            x=temp.index[0:300],
            y=temp['Forecasted Gas (Mcf/d)'].cumsum()[0:300]*365/12,
            name='Cumulative Forecasted Gas',
            line=dict(color='black', dash='dash')
        ), row=1, col=2)

        # Layout
        fig.update_layout(
            height=500, width=1000,
            showlegend=False
        )
        # Update layout
        fig.update_layout(
            xaxis=dict(title='Producing Date', showticklabels=True),
            yaxis=dict(
                title="Mcf/d",
                tickformat=',d'  # No decimals, commas as thousand separators
            )
        )





        fig.update_yaxes(type='log', row=1, col=1)  # Oil cumulative y-axis
        fig.update_yaxes(type='linear', row=1, col=2)  # Gas cumulative y-axis
        fig.update_layout(title_text=i)

        with col2:
            st.plotly_chart(fig)
        
  
        temp_forecast_column = temp[["Forecasted Gas (Mcf/d)"]].rename(columns={"Forecasted Gas (Mcf/d)": i})
        temp_historical_column = temp[["Historical Gas (Mcf/d)"]].rename(columns={"Historical Gas (Mcf/d)": i})


        if forecasts is None:
            forecasts = temp_forecast_column
        else:
            forecasts = forecasts.join(temp_forecast_column, how="outer")
        
        if historicals is None:
            historicals = temp_historical_column
        else:
            historicals = historicals.join(temp_historical_column, how="outer")



    forecasts_sum = forecasts.sum(axis=1)  # Sum across columns (i.e., for each date)
    historicals_sum = historicals.sum(axis=1)

    combined = pd.DataFrame({
    "Forecast": forecasts_sum,
    "Historical": historicals_sum
    }).dropna()
    #combined = combined[combined.index.year <= 2040]
    hist = combined["Historical"]

    # Find the last non-zero value
    last_nonzero_index = hist[hist != 0].last_valid_index()

    # Replace all values after that index (inclusive of trailing zeros) with NaN
    combined.loc[hist.index > last_nonzero_index, "Historical"] = np.nan

    col1, col2 ,col3= st.columns([1, 1, 1])  # center column is wider
    with col1:
        st.write("Historicals")
        st.dataframe(historicals)
    with col2:
        st.write("Forecasts")
        st.dataframe(forecasts)
    with col3:
        st.write("Total Historical and Forecast")
        st.dataframe(combined)


    combined = combined[combined.index.year <= 2030]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=combined.index,
        y=combined["Forecast"],
        mode="lines",
        name="Forecast"
    ))

    fig.add_trace(go.Scatter(
        x=combined.index,
        y=combined["Historical"],
        mode="lines",
        name="Historical"
    ))

    fig.update_layout(
        title="Forecast vs Historical Total Gas",
        xaxis_title="Date",
        yaxis_title="Total Gas (Mcf/d)",
        template="plotly_white"
    )
    fig.update_yaxes(type=scale_type)  # Oil cumulative y-axis
    fig.update_layout(height=600)  # height in pixels

    st.plotly_chart(fig)




else:
    st.warning("Please upload both Well Headers and Production CSV files.")
