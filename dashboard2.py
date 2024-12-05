import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load the dataset
file_path = 'D:\HIWI\Filtered.xlsx'
data = pd.read_excel(file_path)

# Preprocess data
data['Thickness [cm]'] = pd.to_numeric(data['Thickness [cm]'], errors='coerce')
data['λ-Wert [W/(mK)]'] = pd.to_numeric(data['λ-Wert [W/(mK)]'].str.replace(',', '.'), errors='coerce')

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout for the dashboard
app.layout = html.Div([
    html.H1("Construction Materials Dashboard", style={'text-align': 'center'}),
    
    # Dropdowns for filters
    html.Div([
        html.Label("Select Region:"),
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': region, 'value': region} for region in data['Region'].unique()],
            value=data['Region'].unique()[0],
            multi=False,
            style={'width': '50%'}
        ),
        html.Label("Select Construction Age Class:"),
        dcc.Dropdown(
            id='age-class-dropdown',
            options=[{'label': age, 'value': age} for age in data['Construction Age Class'].unique()],
            value=data['Construction Age Class'].unique()[0],
            multi=False,
            style={'width': '50%'}
        ),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

    # Graphs
    html.Div([
        dcc.Graph(id='material-distribution-chart'),
        dcc.Graph(id='thickness-age-chart'),
        dcc.Graph(id='lambda-construction-chart'),
        dcc.Graph(id='component-region-chart'),
    ]),
])

# Callbacks for interactivity
@app.callback(
    [
        Output('material-distribution-chart', 'figure'),
        Output('thickness-age-chart', 'figure'),
        Output('lambda-construction-chart', 'figure'),
        Output('component-region-chart', 'figure'),
    ],
    [
        Input('region-dropdown', 'value'),
        Input('age-class-dropdown', 'value'),
    ]
)
def update_graphs(selected_region, selected_age_class):
    # Filter data based on inputs
    filtered_data = data[(data['Region'] == selected_region) & 
                         (data['Construction Age Class'] == selected_age_class)]
    
    # Chart 1: Material Distribution
    material_chart = px.pie(
        filtered_data, names='Material',
        title='Material Distribution',
        hole=0.3
    )

    # Chart 2: Average Thickness by Material and Age Class
    thickness_chart = px.bar(
        filtered_data.groupby(['Material', 'Construction Age Class'])['Thickness [cm]'].mean().reset_index(),
        x='Material', y='Thickness [cm]', color='Construction Age Class',
        title='Average Thickness by Material and Age Class'
    )

    # Chart 3: λ-Wert by Construction Method
    lambda_chart = px.box(
        filtered_data, x='Construction', y='λ-Wert [W/(mK)]',
        title='Thermal Conductivity by Construction Method',
        labels={'λ-Wert [W/(mK)]': 'Thermal Conductivity (W/(mK))'}
    )

    # Chart 4: Component Distribution by Region
    component_chart = px.bar(
        filtered_data.groupby('Component').size().reset_index(name='Counts'),
        x='Component', y='Counts',
        title='Component Distribution by Region',
        labels={'Counts': 'Count'}
    )

    return material_chart, thickness_chart, lambda_chart, component_chart

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
