import streamlit as st
import pandas as pd

def calculate_thickness(base_thickness, q_value, Q_value):
    max_thickness = 50  # Fixed for Industry (E1/E2)
    thickness_increment = (max_thickness - base_thickness) / (10 - 2)
    adjusted_thickness = base_thickness + (Q_value - 2) * thickness_increment
    return round(adjusted_thickness, 2)

# Streamlit UI
st.title("Building Thickness Calculator")
st.write("Enter the residential building thickness and Q values for other types to calculate relative thickness.")

# User inputs base thickness for residential buildings
residential_thickness = st.number_input("Enter Residential Base Thickness (t) in cm", min_value=5.0, max_value=50.0, value=15.0, step=0.5)

# User inputs Q values for different building types
building_types = ["Offices", "Education", "Culture", "Trade", "Healthcare", "Hospitality", "Industry"]
q_values = {}
for building in building_types:
    q_values[building] = st.number_input(f"Enter Q Value for {building}", min_value=2, max_value=10, value=4, step=1)

# Calculate thickness for each building type
results = {}
for building, Q_value in q_values.items():
    results[building] = calculate_thickness(residential_thickness, 2, Q_value)

# Display results
st.write("### Calculated Thickness for Each Building Type")
st.write(pd.DataFrame(results.items(), columns=["Building Type", "Calculated Thickness (cm)"]))
