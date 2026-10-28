# my_app.py
import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
from geopy.distance import geodesic

# Sample well data
wells = pd.DataFrame({
    "name": ["Well A", "Well B", "Well C"],
    "lat": [29.7, 29.8, 29.75],
    "lon": [-95.3, -95.2, -95.25],
})

# Initialize session state
if "clicked_wells" not in st.session_state:
    st.session_state.clicked_wells = []

# Create base map
m = fl.Map(location=[29.75, -95.25], zoom_start=10)

# Add well markers
for _, row in wells.iterrows():
    fl.Marker(
        location=[row["lat"], row["lon"]],
        popup=row["name"],
        tooltip=row["name"]
    ).add_to(m)

# Enable LatLng click capture
m.add_child(fl.LatLngPopup())

# Display map
map_data = st_folium(m, height=400, width=700)

# Process clicks
if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lng = map_data["last_clicked"]["lng"]
    clicked_point = (clicked_lat, clicked_lng)

    def find_nearest_well():
        for _, row in wells.iterrows():
            well_point = (row["lat"], row["lon"])
            dist = geodesic(clicked_point, well_point).meters
            if dist < 500:  # Click tolerance
                return row["name"]
        return None

    well_clicked = find_nearest_well()

    if well_clicked:
        if well_clicked in st.session_state.clicked_wells:
            st.session_state.clicked_wells.remove(well_clicked)
            st.toast(f"❌ Removed: {well_clicked}")
        else:
            st.session_state.clicked_wells.append(well_clicked)
            st.toast(f"✅ Added: {well_clicked}")

# Show clicked wells
st.divider()
st.markdown("### 🛢️ Wells Clicked")
if st.session_state.clicked_wells:
    st.write(st.session_state.clicked_wells)
else:
    st.write("No wells selected yet.")
