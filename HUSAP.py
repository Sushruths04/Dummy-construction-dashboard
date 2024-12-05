import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
file_path = 'D:\HIWI\Filtered.xlsx'
data = pd.read_excel(file_path)

# Preprocess data
data['Thickness [cm]'] = pd.to_numeric(data['Thickness [cm]'], errors='coerce')
data['λ-Wert [W/(mK)]'] = pd.to_numeric(data['λ-Wert [W/(mK)]'].str.replace(',', '.'), errors='coerce')

# Sidebar for filtering
st.sidebar.header("Filters")
region = st.sidebar.selectbox("Select Region", data['Region'].unique())
age_class = st.sidebar.selectbox("Select Construction Age Class", data['Construction Age Class'].unique())

# Filter data
filtered_data = data[(data['Region'] == region) & (data['Construction Age Class'] == age_class)]

# Title
st.title("Construction Materials Dashboard")

# 1. Material Distribution Pie Chart
st.subheader("Material Distribution")
material_chart = px.pie(filtered_data, names='Material', title='Material Distribution', hole=0.3)
st.plotly_chart(material_chart, use_container_width=True)

# 2. Average Thickness by Material
st.subheader("Average Thickness by Material")
thickness_chart = px.bar(
    filtered_data.groupby(['Material'])['Thickness [cm]'].mean().reset_index(),
    x='Material', y='Thickness [cm]', title='Average Thickness by Material'
)
st.plotly_chart(thickness_chart, use_container_width=True)

# 3. λ-Wert by Construction Method
st.subheader("Thermal Conductivity by Construction Method")
lambda_chart = px.box(filtered_data, x='Construction', y='λ-Wert [W/(mK)]', title='Thermal Conductivity by Construction Method')
st.plotly_chart(lambda_chart, use_container_width=True)

# 4. Component Distribution
st.subheader("Component Distribution")
component_chart = px.bar(
    filtered_data.groupby('Component').size().reset_index(name='Counts'),
    x='Component', y='Counts', title='Component Distribution'
)
st.plotly_chart(component_chart, use_container_width=True)
