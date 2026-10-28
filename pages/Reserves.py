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
def arps(t, qi, db, n, de=.06):
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

    wells = pd.read_csv("West AOI - Lower Eagle Ford Well Headers.CSV")
    prod= pd.read_csv("West AOI - Lower Eagle Ford Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    wells = pd.read_csv("South AOI - Austin Chalk Well Headers.CSV")
    prod= pd.read_csv("South AOI - Austin Chalk Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("South AOI - Lower Eagle Ford Well Headers.CSV")
    #prod= pd.read_csv("South AOI - Lower Eagle Ford Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("East AOI - Lower Eagle Ford Well Headers.CSV")
    #prod= pd.read_csv("East AOI - Lower Eagle Ford Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("Warwick Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("Warwick Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("Devon Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("Devon Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("Repsol Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("Repsol Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    #wells = pd.read_csv("Repsol All Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("Repsol All Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    
    #wells = pd.read_csv("1776 Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("1776 Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})


    #wells = pd.read_csv("Magnolia Ironwood PDP Well Headers.CSV")
    #prod= pd.read_csv("Magnolia Ironwood PDP Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("morrow Well Headers.CSV")
    #prod= pd.read_csv("morrow Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("TC West AOI Check 2 Well Headers.CSV")
    #prod= pd.read_csv("TC West AOI Check 2 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    
    
    wells = pd.read_csv("Austin Chalk TC 2500+ proppant  Well Headers.CSV")
    prod= pd.read_csv("Austin Chalk TC 2500+ proppant  Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})




    wells = pd.read_csv("Austin Chalk TC Area Well Headers.CSV")
    prod= pd.read_csv("Austin Chalk TC Area Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    

    wells = pd.read_csv("Austin Chalk Tier 2 Well Headers.CSV")
    prod= pd.read_csv("Austin Chalk Tier 2 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    

    #wells = pd.read_csv("Austin Chalk TC v2 Well Headers.CSV")
    #prod= pd.read_csv("Austin Chalk TC v2 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    #wells = pd.read_csv("Austin Chalk Tier 1 Well Headers.CSV")
    #prod= pd.read_csv("Austin Chalk Tier 1 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})

    
    wells = pd.read_csv("Austin Chalk TC v3 Well Headers.CSV")
    prod= pd.read_csv("Austin Chalk TC v3 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
        
    wells = pd.read_csv("Magnolia Eagle Ford Karnes Post 2020 Well Headers.CSV")
    prod= pd.read_csv("Magnolia Eagle Ford Karnes Post 2020 Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    
    #wells = pd.read_csv("Magnolia 2023-2024 Eagle Ford Wells Well Headers.CSV")
    #prod= pd.read_csv("Magnolia 2023-2024 Eagle Ford Wells Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    
    wells = pd.read_csv("Karnes 2015+ in trough wells Well Headers.CSV")
    prod= pd.read_csv("Karnes 2015+ in trough wells Well Monthly Production.CSV").rename(columns={'API/UWI': 'API14'})
    


    
    
    wells = wells[wells['API14']!=42255378050000]
    prod = prod[prod['API14']!=42255378050000]
    

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


#########################################################################################################################################################################################################
    st.header("Well Performance Summary")
    st.dataframe(wells)
    # Drop rows with missing values
    wells_filtered = wells.dropna(subset=[
        'Completion Date',
        'DI Lateral Length',
        'Proppant per Perforated Foot (First Treatment Job)',
        'EUR (BE) Oil per perforated Ft',
        'EUR (BE) Gas per perforated Ft',
        'Operator Company Name',
        'Well Name',
        'Well Number'
    ])
    wells_filtered=wells
    # Create numeric x for regression
    wells_filtered['Completion Timestamp'] = wells_filtered['Completion Date'].astype(np.int64) // 10**9  # seconds

    # Setup figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'DI Lateral Length vs Completion Date',
            'Proppant per Perf Foot vs Completion Date',
            'EUR (BE) Oil per perforated Ft vs Completion Date',
            'EUR (BE) Gas per perforated Ft vs Completion Date'
        ],
        shared_xaxes=True,
        vertical_spacing=0.08  # Reduced from default 0.3
    )

    # Hover text
    hover_text = (
        "<b>Operator:</b> " + wells_filtered['Operator Company Name'] + "<br>" +
        "<b>Well Name:</b> " + wells_filtered['Well Name'] + "<br>" +
        "<b>API:</b> " + wells_filtered['API14_formatted'].astype(str)
    )
    # Helper to add scatter + trendline
    def add_plot(x_dates, x_numeric, y, label, row, col):
        # Scatter
        fig.add_trace(go.Scatter(
            x=x_dates,
            y=y,
            mode='markers',
            name=label,
            text=hover_text,
            hovertemplate="<b>%{text}</b><br>" +
                        "Completion Date: %{x|%Y-%m-%d}<br>" +
                        label + ": %{y:.2f}<extra></extra>"
        ), row=row, col=col)

        # Linear trendline
        z = np.polyfit(x_numeric, y, 1)
        p = np.poly1d(z)
        x_range = np.linspace(x_numeric.min(), x_numeric.max(), 100)
        x_range_dates = pd.to_datetime(x_range, unit='s')

        fig.add_trace(go.Scatter(
            x=x_range_dates,
            y=p(x_range),
            mode='lines',
            name=f'{label} Trend',
            line=dict(dash='dash', color='black'),
            showlegend=False
        ), row=row, col=col)

    try:
        add_plot(
            wells_filtered['Completion Date'],
            wells_filtered['Completion Timestamp'],
            wells_filtered['DI Lateral Length'],
            'Lateral Length',
            row=1, col=1
        )
    except:
        pass
    try:
        add_plot(
            wells_filtered['Completion Date'],
            wells_filtered['Completion Timestamp'],
            wells_filtered['Proppant per Perforated Foot (First Treatment Job)'],
            'Proppant per Perf Ft',
            row=1, col=2
        )
    except:
        pass
    try:
        add_plot(
            wells_filtered['Completion Date'],
            wells_filtered['Completion Timestamp'],
            wells_filtered['EUR (BE) Oil per perforated Ft'],
            'EUR (BE) Oil per perforated Ft',
            row=2, col=1
        )
    except:
        pass
    try:
        add_plot(
            wells_filtered['Completion Date'],
            wells_filtered['Completion Timestamp'],
            wells_filtered['EUR (BE) Gas per perforated Ft'],
            'EUR (BE) Gas per perforated Ft',
            row=2, col=2
        )
    except:
        pass

    # Final layout
    fig.update_layout(
        height=800,
        width=1000,
        showlegend=False
    )

   
    st.plotly_chart(fig)

    st.dataframe(wells_filtered)
    # Raw values
    values = [
            wells_filtered['DI Lateral Length'].mean(),
            wells_filtered['Proppant per Perforated Foot (First Treatment Job)'].mean(),
            wells_filtered['EUR Oil (BE)'].mean(),
            wells_filtered['EUR Gas (BE)'].mean(),  # optional to remove
            wells_filtered['Gross Perforated Interval'].mean(),
            wells_filtered['EUR (BE) Oil per perforated Ft'].mean(),
            wells_filtered['EUR (BE) Gas per perforated Ft'].mean(),
            wells_filtered['EUR (BE) Oil per perforated Ft'].median(),
            wells_filtered['EUR (BE) Gas per perforated Ft'].median()
    ]

    formatted_values = [
        f"{v:,.0f}" if i < 5 else f"{v:,.2f}"
        for i, v in enumerate(values)
    ]

    metrics = [
        "Average Lateral Length (ft)",
        "Average Proppant per Perf Foot (lb/ft)",
        "Average EUR Oil (BE) (Bbl)",
        "Average EUR Gas (BE) (Mcf)",
        "Average Gross Perf Interval (ft)",
        "Avg EUR Oil (BE) per Perf Foot (bbl/ft)",
        "Avg EUR Gas (BE) per Perf Foot (Mcf/ft)",
        "Median EUR Oil (BE) per Perf Foot (bbl/ft)",
        "Median EUR Gas (BE) per Perf Foot (Mcf/ft)"
    ]

    # DataFrame with no index shown
    summary_df = pd.DataFrame({
        "Metric": metrics,
        "Value": formatted_values
    })


    # Display in Streamlit

    col1, col2, col3 = st.columns([1, 1, 1])  # center column is wider
    with col2:
        st.table(summary_df.reset_index(drop=True))






#type curve 
##########################################################################################################################################################################################################

    st.markdown("---")
    st.header("Normalized Type Curves")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        lateralLength = st.number_input(
            "Enter Lateral Length(ft) for Normalization", 
            min_value=1, 
            max_value=50000, 
            value=7500, 
            step=100, 
            format="%d"
        )
        st.write(f"Normalizing to: {lateralLength}'")


#get average and daily data
#########################################################################################################################################################################################################
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        option = st.selectbox("Choose:", ["Mean", "Median"])
        st.write("You selected:", option)


        
    # Pivot tables
    gasD = prod.pivot_table(index='Producing Month Number', columns='Well Name', values='Daily Avg Gas Per perforated Ft').sort_index()
    oilD = prod.pivot_table(index='Producing Month Number', columns='Well Name', values='Daily Avg Oil Per perforated Ft').sort_index()

    # Sum across wells
    avg_gasD = gasD.mean(axis=1)*lateralLength ##daily production
    avg_oilD = oilD.mean(axis=1)*lateralLength ## daily production

    if option == "Median":
        avg_gasD = gasD.median(axis=1)*lateralLength ##Monthly production
        avg_oilD = oilD.median(axis=1)*lateralLength ## Monthly production


    gas_weights = np.ones(len(gasD))#gasD.count(axis=1).values
    oil_weights = np.ones(len(gasD))#gasD.count(axis=1).values



    gasM = prod.pivot_table(index='Producing Month Number', columns='Well Name', values='Monthly Gas Per perforated Ft').sort_index()
    oilM = prod.pivot_table(index='Producing Month Number', columns='Well Name', values='Monthly Oil Per perforated Ft').sort_index()

    # Sum across wells
    avg_gasM = gasM.mean(axis=1)*lateralLength ##Monthly production
    avg_oilM = oilM.mean(axis=1)*lateralLength ## Monthly production
    if option == "Median":
        avg_gasM = gasM.median(axis=1)*lateralLength ##Monthly production
        avg_oilM = oilM.median(axis=1)*lateralLength ## Monthly production




    def fit(dailyRates, weights):
        initial_guess = [np.max(dailyRates.values)*1, 0.9, 1.1]
        bounds = ([.0, .3, .5], [np.max(dailyRates.values)*2, .99, 1.3])

        # Fit the data using curve_fit
        params, covariance = curve_fit(arps, dailyRates[1:].index.values, dailyRates[1:].values,bounds = bounds, sigma = 1/weights[1:], p0=initial_guess)

        # Extract the fitted parameters
        qi_fit, db_fit, n_fit = params
        #st.write(f"Avg Gas Fitted Parameters: qi = {qi_fit}, db = {db_fit}, n = {n_fit}")

        # Generate the fitted production data
        production_fitted = np.array(arps(dailyRates[1:].index.values, *params))
        return production_fitted, qi_fit, db_fit, n_fit
    

    gas_production_fitted, gas_qi_fit, gas_db_fit, gas_n_fit = fit(avg_gasD, gas_weights)
    gas_50_year = arps(np.zeros(599), gas_qi_fit,gas_db_fit, gas_n_fit)


    oil_production_fitted, oil_qi_fit, oil_db_fit, oil_n_fit = fit(avg_oilD, oil_weights)
    oil_50_year = arps(np.zeros(599), oil_qi_fit,oil_db_fit, oil_n_fit)




    #st.write(f"Avg Normalized Gas Fitted Parameters: qi = {np.round(gas_qi_fit, 2)}, db = {np.round(gas_db_fit, 4)}, n = {np.round(gas_n_fit,4)}")
    #st.write(f"Avg Normalized Gas EUR = {gas_50_year.sum() * 365 / 12:,.0f}")
    #st.write(f"Avg Normalized Oil Fitted Parameters: qi = {np.round(oil_qi_fit, 2)}, db = {np.round(oil_db_fit, 4)}, n = {np.round(oil_n_fit,4)}")
    #st.write(f"Avg Noramlized Oil EUR = {oil_50_year.sum() * 365 / 12:,.0f}")
    # Format numbers with commas and proper precision
    data = {
        "EUR (Mcf/Bbl)": [f"{gas_50_year.sum()*365/12:,.0f}", f"{oil_50_year.sum()*365/12:,.0f}"],
        "qi": [f"{gas_qi_fit:,.2f}", f"{oil_qi_fit:,.2f}"],
        "db": [f"{gas_db_fit:.4f}", f"{oil_db_fit:.4f}"],
        "n": [f"{gas_n_fit:.4f}", f"{oil_n_fit:.4f}"],
        "de": [f"{.06:.2f}", f"{.06:.2f}"]
    }

    df = pd.DataFrame(data, index=["Gas", "Oil"])

    col1, col2, col3 = st.columns([1, 1, 1])  # center column is wider
    with col2:
        # Display as styled table without index column (optional)
        st.dataframe(df.style.set_table_styles(
            [{"selector": "th", "props": [("text-align", "center")]}]
        ).set_properties(**{"text-align": "center"}), use_container_width=True)


    gas_50_year = np.insert(gas_50_year, 0, np.nan)
    oil_50_year = np.insert(oil_50_year, 0, np.nan)

    gas_fitted_padded = np.pad(avg_gasD, (0, 600 - len(avg_gasD)), constant_values=np.nan)
   # oil_fitted_padded = np.pad(oil_fitted, (0, 600 - len(oil_fitted)), constant_values=np.nan)

    tc = pd.DataFrame({
        "Month": range(1, 601),
        "Gas Type Curve (Mcf/d)": gas_50_year,
        "Oil Type Curve (Bbls/d)": oil_50_year

    })
    tc.index = tc['Month']
    tc['Average Gas (Mcf/d)']= pd.Series(avg_gasD)
    tc['Average Oil (Bbls/d)']= pd.Series(avg_oilD)
    tc['Gas Type Curve (Mcf/d)'].iloc[0]=tc['Average Gas (Mcf/d)'].iloc[0]
    tc['Oil Type Curve (Bbls/d)'].iloc[0]=tc['Average Oil (Bbls/d)'].iloc[0]


    col1, col2, col3 = st.columns([1, 3, 1])  # center column is wider
    with col2:
        st.dataframe(tc)

#2x2 plots of rate and cum
##########################################################################################################################################################################################################


        # Plot
    # Create the subplots with 4 rows and 4 columns
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles = [
            f"Oil - Daily Avg Norm ({lateralLength}')",
            f"Oil - Cumulative Avg Norm ({lateralLength}')",
            f"Gas - Daily Avg Norm ({lateralLength}')",
            f"Gas - Cumulative Avg Norm ({lateralLength}')"
        ],
        shared_xaxes=True
    )



    well_line_style = dict(color='lightgray', dash='dot', width=1)
    dash_opacity = .5

###############################################################################
    # Daily Avg - Oil (Top-left) - All Wells - grey dashed lines
    for col in oilD.columns:
        fig.add_trace(go.Scatter(
            x=oilD.index,
            y=oilD[col] * lateralLength,
            mode='lines',
            line=dict(color='grey', dash='dash', width=1),
            opacity=dash_opacity,
            showlegend=False,
            hovertemplate="<b>"+str(col)+"</b><br>Month: %{x}<br>Rate: %{y:,.0f} BBL/day<extra></extra>",
            hoverinfo= 'text'
        ), row=1, col=1)
    #Average Daily Oil (Top-left) - Single solid green line
    fig.add_trace(go.Scatter(
        x=avg_oilD.index,
        y=avg_oilD,
        mode='lines',
        name='Oil Daily Avg',
        line=dict(color='green')
    ), row=1, col=1)

    #Monthly Oil Cum (Top-right) - All Wells - grey dashed lines
    for col in oilM.columns:
        fig.add_trace(go.Scatter(
            x=oilM.index,
            y=oilM[col].cumsum() * lateralLength,
            mode='lines',
            line=dict(color='grey', dash='dash', width=1),
            opacity=dash_opacity,
            showlegend=False,
            hovertemplate="<b>"+str(col)+"</b><br>Month: %{x}<br>Cum: %{y:,.0f} Bbl<extra></extra>",
            hoverinfo= 'text'
        ), row=1, col=2)
    #Average Oil Cum (Top-right) - solid green line
    fig.add_trace(go.Scatter(
        x=avg_oilM.index,
        y=avg_oilM.cumsum(),
        mode='lines',
        name='Oil Cumulative',
        line=dict(color='green')
    ), row=1, col=2)

    #Average Daily Oil Fit (Top-left) - Single solid black line
    fig.add_trace(go.Scatter(
        x=tc['Month'][:len(avg_oilD)],
        y=tc['Oil Type Curve (Bbls/d)'][:len(avg_oilD)],
        mode='lines',
        name='Curve Fit Oil Daily',
        line=dict(color='black', dash = "dash")
    ), row=1, col=1)




   #Average Oil Cum Fit (Top-right) - solid black line
    fig.add_trace(go.Scatter(
        x=tc['Month'][:len(avg_gasD)],
        y=np.cumsum(tc['Oil Type Curve (Bbls/d)']*365/12)[:len(avg_oilD)],
        mode='lines',
        name='Oil Cumulative Fit',
        line=dict(color='black', dash = 'dash')
    ), row=1, col=2)






   ###############################################################################
    #Daily Avg - Gas (Bot-left) - All Wells - grey dashed lines
    for col in gasD.columns:
        fig.add_trace(go.Scatter(
            x=gasD.index,
            y=gasD[col] * lateralLength,
            mode='lines',
            line=dict(color='grey', dash='dash', width=1),
            opacity=dash_opacity,
            showlegend=False,
            hovertemplate="<b>"+str(col)+"</b><br>Month: %{x}<br>Rate: %{y:,.0f} Mcf/d<extra></extra>",
            hoverinfo= 'text'
        ), row=2, col=1)




    #Average Daily Gas (Bot-left) - Single solid red line

    fig.add_trace(go.Scatter(
        x=avg_gasD.index,
        y=avg_gasD,
        mode='lines',
        name='Gas Daily Avg',
        line=dict(color='red')
    ), row=2, col=1)

    #Average Daily Gas Fit (Bot-left) - Single solid black line
    fig.add_trace(go.Scatter(
        x=tc['Month'][:len(avg_gasD)],
        y=tc['Gas Type Curve (Mcf/d)'][:len(avg_gasD)],
        mode='lines',
        name='Curve Fit Gas Daily',
        line=dict(color='black', dash = "dash")
    ), row=2, col=1)











    #Monthly Gas Cum (Bot-right) - All Wells - grey dashed lines
    for col in gasM.columns:
        fig.add_trace(go.Scatter(
            x=gasM.index,
            y=gasM[col].cumsum() * lateralLength,
            mode='lines',
            line=dict(color='grey', dash='dash', width=1),
            opacity=dash_opacity,
            showlegend=False,
            hovertemplate="<b>"+str(col)+"</b><br>Month: %{x}<br>Cum: %{y:,.0f} Mcf<extra></extra>",
            hoverinfo= 'text'
        ), row=2, col=2)
    #Average Gas Cum (Bot-right) - solid red line
    fig.add_trace(go.Scatter(
        x=avg_gasM.index,
        y=avg_gasM.cumsum(),
        mode='lines',
        name='Gas Cumulative',
        line=dict(color='red')
    ), row=2, col=2)

    #Average Gas Cum Fit (Bot-right) - solid black line
    fig.add_trace(go.Scatter(
        x=tc['Month'][:len(avg_gasD)],
        y=np.cumsum(tc['Gas Type Curve (Mcf/d)']*365/12)[:len(avg_gasD)],
        mode='lines',
        name='Gas Cumulative Fit',
        line=dict(color='black', dash = 'dash')
    ), row=2, col=2)


   ###############################################################################







    # Update layout
    fig.update_layout(
        height=850,
        width=800,
        showlegend=False,
        xaxis=dict(title='Producing Month', showticklabels=True),
        yaxis=dict(
            title="BBLs/day",
            tickformat=',d'  # No decimals, commas as thousand separators
        ),
        xaxis2=dict(title='Producing Month', showticklabels=True),
        yaxis2=dict(
            title="BBLs",
            tickformat=',d'
        ),
        xaxis3=dict(title='Producing Month', showticklabels=True),
        yaxis3=dict(
            title="MCFD",
            tickformat=',d'
        ),
        xaxis4=dict(title='Producing Month', showticklabels=True),
        yaxis4=dict(
            title="MCF",
            tickformat=',d'
        ),
    )


    scale_type = st.radio("Rate Y-axis Scale", ["log", "linear"])
    # Set the y-axes to logarithmic scale for better visualization of the cumulative values
    fig.update_yaxes(type=scale_type, row=2, col=1)  # Oil cumulative y-axis
    fig.update_yaxes(type='linear', row=2, col=2)  # Gas cumulative y-axis
    # Set the y-axes to logarithmic scale for better visualization of the cumulative values
    fig.update_yaxes(type=scale_type, row=1, col=1)  # Oil cumulative y-axis
    fig.update_yaxes(type='linear', row=1, col=2)  # Gas cumulative y-axis

    # Show the plot in Streamlit
    st.plotly_chart(fig)


















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


    tc_gas_db_fit=gas_db_fit
    tc_gas_n_fit =gas_n_fit
    def fit(dailyRates, weight = False):

        cleaned = dailyRates.dropna()
        x = np.arange(len(cleaned))[1:]         # skip first point
        y = cleaned.values[1:]                  # skip first point
        weights = np.ones(len(x))
        if weight:
            weights =  np.exp(np.linspace(0, 3, len(x)))
               
        


        initial_guess = [np.max(y), tc_gas_db_fit, tc_gas_n_fit]
        bounds = ([.001, .3, .6], [np.max(y)*2.5, .99, 1.2])

        # Fit the data using curve_fit
        params, covariance = curve_fit(arps,x, y,bounds = bounds, sigma = 1/weights, p0=initial_guess)

        # Extract the fitted parameters
        qi_fit, db_fit, n_fit = params
        #st.write(f"Avg Gas Fitted Parameters: qi = {qi_fit}, db = {db_fit}, n = {n_fit}")

        # Generate the fitted production data
        production_fitted = np.array(arps(x, *params))
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





        fig.update_yaxes(type=scale_type, row=1, col=1)  # Oil cumulative y-axis
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
