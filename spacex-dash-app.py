# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True,
        style={'width': '80%', 'margin': 'auto'}
    ),
    html.Br(),

    # TASK 2: Pie chart for success rates
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),
    
    # TASK 3: Range slider for payload selection
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload],
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.Br(),

    # TASK 4: Scatter chart for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart - CORRECTED VERSION
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, show success count by launch site
        # Filter only successful launches (class = 1) and count by launch site
        success_by_site = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        
        fig = px.pie(
            names=success_by_site.index,
            values=success_by_site.values,
            title='Total Success Launches by Site',
            color=success_by_site.index
        )
    else:
        # For specific site, show success vs failure for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df, 
            names='class',
            title=f'Launch Success Rate for {entered_site}',
            color='class',
            color_discrete_map={0: 'red', 1: 'green'}
        )
    
    # Update layout for better appearance
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter by payload range first
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Then filter by site if needed
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Booster Version'],
        title=f'Payload vs Launch Success ({selected_site})' if selected_site != 'ALL' else 'Payload vs Launch Success (All Sites)',
        labels={
            'class': 'Launch Outcome',
            'Payload Mass (kg)': 'Payload Mass (kg)'
        }
    )
    
    # Customize y-axis to show meaningful labels
    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=['Failure', 'Success']
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Launch Outcome'
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
