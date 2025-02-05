import streamlit as st
import pandas as pd

def calculate_thickness(base_thickness, q_value, Q_value):
    max_thickness = 50  # Fixed for Industry (E1/E2)
    thickness_increment = (max_thickness - base_thickness) / (10 - 2)
    adjusted_thickness = base_thickness + (Q_value - 2) * thickness_increment
    return round(adjusted_thickness, 2)

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Building Thickness Calculator")

# Layout in columns to fit everything on a single screen
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input Parameters")
    residential_thickness = st.number_input("Enter Residential Base Thickness (t) in cm", min_value=5.0, max_value=50.0, value=15.0, step=0.5)

    building_types = ["Offices", "Education", "Culture", "Trade", "Healthcare", "Hospitality", "Industry"]
    q_values = {building: st.number_input(f"Enter Q Value for {building}", min_value=2, max_value=10, value=4, step=1) for building in building_types}

with col2:
    st.header("Results")
    results = {building: calculate_thickness(residential_thickness, 2, Q_value) for building, Q_value in q_values.items()}
    st.write(pd.DataFrame(results.items(), columns=["Building Type", "Calculated Thickness (cm)"]))
