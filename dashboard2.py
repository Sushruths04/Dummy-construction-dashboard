import pandas as pd
import streamlit as st
import plotly.express as px

# Load and clean the dataset
@st.cache
def load_data():
    file_path = "updated_baualtersklasses.xlsx"  # Updated
    df = pd.read_excel(file_path)
    df['Stärke [cm]'] = df['Stärke [cm]'].replace(',', '.', regex=True)
    df['λ-Wert [W/(mK)]'] = df['λ-Wert [W/(mK)]'].replace(',', '.', regex=True)
    df['Stärke [cm]'] = pd.to_numeric(df['Stärke [cm]'], errors='coerce')  # Convert to float, replace invalid entries with NaN
    df['λ-Wert [W/(mK)]'] = pd.to_numeric(df['λ-Wert [W/(mK)]'], errors='coerce')  # Same for lambda values
    return df

data = load_data()

# Define the correct order for Baualtersklasse
time_order = [
    "Bis 1918", "1919-1948", "1949-1957", "1958-1968", 
    "1969-1978", "1979-1983", "1984-1994"
]

# Apply ordering to Baualtersklasse in the dataset
data['Baualtersklasse'] = pd.Categorical(data['Baualtersklasse'], categories=time_order, ordered=True)

# Title
st.title("Building Material Analysis Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Select Region", options=data['Region'].unique(), default=data['Region'].unique())
# Get unique years (Baualtersklasse) and ensure no NaN values
valid_years = data['Baualtersklasse'].dropna().unique()

# Convert to list to avoid issues with default values
valid_years = list(valid_years)

# Sidebar multiselect for years
years = st.sidebar.multiselect(
    "Select Years",
    options=valid_years,  # Use valid unique years
    default=valid_years   # Set all valid years as default
)

bauteil = st.sidebar.multiselect("Select Bauteil", options=data['Bauteil'].unique(), default=data['Bauteil'].unique())

konstruktion = st.sidebar.multiselect("Select Konstruktion", options=data['Konstruktion'].unique(), default=data['Konstruktion'].unique())


# Filtered Data
filtered_data = data[(data['Region'].isin(regions)) & 
                     (data['Baualtersklasse'].isin(years)) & 
                     (data['Bauteil'].isin(bauteil)) &
                     (data['Konstruktion'].isin(konstruktion))]

# Display Metrics
st.subheader("Average Metrics")
avg_thickness = filtered_data['Stärke [cm]'].mean()
avg_lambda = filtered_data['λ-Wert [W/(mK)]'].mean()
st.metric("Average Thickness (cm)", f"{avg_thickness:.2f}")
st.metric("Average Lambda Value (W/mK)", f"{avg_lambda:.2f}")

# Pie Chart: Material Distribution (Top 10 Materials)
st.subheader("Material Distribution (Top 10)")
material_counts = filtered_data['Material'].value_counts().reset_index()
material_counts.columns = ['Material', 'Count']

# Group "Others"
top_materials = material_counts[:10]
others = material_counts[10:]
top_materials.loc[len(top_materials)] = ['Others', others['Count'].sum()]

fig_pie = px.pie(top_materials, names='Material', values='Count', title="Material Distribution")
st.plotly_chart(fig_pie)

# Drill-Down: Details for "Others"
if st.button("Show Details for Others"):
    st.subheader("Materials in 'Others'")
    # Display list of materials in "Others"
    st.write(others)
    
    # Create a horizontal bar chart for materials in "Others"
    fig_others = px.bar(others, x='Count', y='Material', orientation='h', title="Material Distribution for 'Others'")
    st.plotly_chart(fig_others)

# Top 10 Materials by Average Thickness and Lambda Value
st.subheader("Top 10 Materials by Average Thickness and Lambda Value")
top_10_avg_materials = (
    filtered_data.groupby('Material')
    .agg(Average_Thickness=('Stärke [cm]', 'mean'), Average_Lambda=('λ-Wert [W/(mK)]', 'mean'))
    .sort_values(by='Average_Thickness', ascending=False)
    .head(20)
    .reset_index()
)
st.write(top_10_avg_materials)

# Trends: Thickness and Lambda Over Time
st.subheader("Trends: Thickness and Lambda Over Time")
trend_data = filtered_data.groupby('Baualtersklasse').agg({'Stärke [cm]': 'mean', 'λ-Wert [W/(mK)]': 'mean'}).reset_index()

fig_trend_thickness = px.line(trend_data, x='Baualtersklasse', y='Stärke [cm]', title="Thickness Trends Over Time")
fig_trend_lambda = px.line(trend_data, x='Baualtersklasse', y='λ-Wert [W/(mK)]', title="Lambda Value Trends Over Time")

st.plotly_chart(fig_trend_thickness)
st.plotly_chart(fig_trend_lambda)

# Enhanced Visualization: Bubble Chart for Lambda Value
st.subheader("Bubble Chart: Lambda Value by Material")
bubble_data = (
    filtered_data.groupby('Material')
    .agg({'Stärke [cm]': 'mean', 'λ-Wert [W/(mK)]': 'mean'})
    .reset_index()
)
# Replace NaN values in 'Stärke [cm]' to avoid invalid sizes in the bubble chart
bubble_data['Stärke [cm]'] = bubble_data['Stärke [cm]'].fillna(0)

fig_bubble = px.scatter(
    bubble_data,
    x='Material',
    y='λ-Wert [W/(mK)]',
    size='Stärke [cm]',  # Bubble size based on average thickness
    title="Lambda Value by Material with Thickness as Bubble Size",
    hover_name='Material'
)
st.plotly_chart(fig_bubble)


# Stacked Bar Chart: Material Usage Trends by Bauteil
st.subheader("Number of Materials Usage Trends by Bauteil")
usage_trends = filtered_data.groupby(['Bauteil', 'Baualtersklasse'])['Material'].count().reset_index()
fig_stack = px.bar(usage_trends, x='Baualtersklasse', y='Material', color='Bauteil', title="Number of Materials Usage Trends by Bauteil", barmode='stack')
st.plotly_chart(fig_stack)


# Correlation Between Materials and Regions
st.subheader("Correlation Between Materials and Regions")

# Aggregate data: Count occurrences of each material by region
correlation_data = filtered_data.groupby(['Region', 'Material']).size().unstack(fill_value=0)

# Regional Analysis
st.subheader("Regional Analysis")

# Filter data by selected region(s)
regional_data = filtered_data[filtered_data['Region'].isin(regions)]

# Material Usage Trends Over Time for Selected Regions
st.subheader("Material Usage Trends Over Time (Selected Regions)")
material_trends = regional_data.groupby(['Baualtersklasse', 'Material']).size().reset_index(name='Count')
fig_material_trends = px.bar(
    material_trends,
    x='Baualtersklasse',
    y='Count',
    color='Material',
    title="Material Usage Trends Over Time (Selected Regions)",
    barmode='stack'
)
st.plotly_chart(fig_material_trends)

# Average Thickness and Lambda Values by Material in Selected Regions
st.subheader("Average Thickness and Lambda Values by Material (Selected Regions)")
avg_metrics = regional_data.groupby('Material').agg({
    'Stärke [cm]': 'mean',
    'λ-Wert [W/(mK)]': 'mean'
}).reset_index()

# Bar chart for average thickness
fig_avg_thickness = px.bar(
    avg_metrics,
    x='Material',
    y='Stärke [cm]',
    title="Average Thickness by Material (Selected Regions)",
    labels={'Stärke [cm]': 'Average Thickness (cm)'},
    color='Material'
)
st.plotly_chart(fig_avg_thickness)

# Bar chart for average lambda values
fig_avg_lambda = px.bar(
    avg_metrics,
    x='Material',
    y='λ-Wert [W/(mK)]',
    title="Average Lambda Value by Material (Selected Regions)",
    labels={'λ-Wert [W/(mK)]': 'Average Lambda (W/mK)'},
    color='Material'
)
st.plotly_chart(fig_avg_lambda)

# Material Usage Comparison Across Regions
# Improved Material Usage Comparison Across Regions
st.subheader("Enhanced Material Usage Comparison Across Regions")

# Filter for significant materials (e.g., materials used more than 10 times)
filtered_comparison = filtered_data.groupby(['Region', 'Material']).size().reset_index(name='Count')
significant_materials = filtered_comparison.groupby('Material')['Count'].sum()
significant_materials = significant_materials[significant_materials > 10].index
filtered_comparison = filtered_comparison[filtered_comparison['Material'].isin(significant_materials)]

# Pivot the data for heatmap
heatmap_data = filtered_comparison.pivot(index='Material', columns='Region', values='Count').fillna(0)

# Create an enhanced heatmap
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Region", y="Material", color="Usage Count"),
    title="Enhanced Material Usage Comparison Across Regions",
    color_continuous_scale="Viridis",
    aspect="auto"
)

# Add annotations for counts
fig_heatmap.update_traces(texttemplate="%{z:.0f}", textfont_size=12)

# Display heatmap
st.plotly_chart(fig_heatmap)

# Normalize Material Usage Trends by Total Records
st.subheader("Proportional Material Usage Trends by Bauteil")

# Calculate total records per Baualtersklasse
total_records = filtered_data.groupby('Baualtersklasse').size()

# Aggregate material usage counts and normalize
usage_trends = (
    filtered_data.groupby(['Bauteil', 'Baualtersklasse'])['Material']
    .count()
    .reset_index()
    .rename(columns={'Material': 'Count'})
)
usage_trends = usage_trends.merge(
    total_records.rename("Total_Records"), on="Baualtersklasse"
)
usage_trends['Proportion'] = usage_trends['Count'] / usage_trends['Total_Records']

# Plot normalized data
fig_normalized = px.bar(
    usage_trends,
    x='Baualtersklasse',
    y='Proportion',
    color='Bauteil',
    title="Proportional Material Usage Trends by Bauteil",
    barmode='stack',
    labels={'Proportion': 'Proportion of Materials Used'}
)
st.plotly_chart(fig_normalized)


# Display Filtered Data Table
st.subheader("Filtered Data")
st.dataframe(filtered_data)
