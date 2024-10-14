# Import necessary libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data from a CSV file
df = pd.read_csv('bio_by_sport_male.csv')

# Define the constants
EVENTS = df['Event'].unique()
ATTRIBUTES = df.columns.drop(['Event', 'Cluster']).tolist()
TITLE = 'Olympics Data Scatterplot'

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1(TITLE, style={'textAlign': 'center'}),
    html.Div([
        # Dropdown menu for selecting the event
        html.Label('Select Event:'),
        dcc.Dropdown(
            id='event',
            options=[
                        {'label': 'All Events', 'value': 'all'}
                    ] + [{'label': event, 'value': event} for event in EVENTS],
            value='all'
        ),

        # Dropdown menu for selecting the x attribute
        html.Label('Select X Attribute:'),
        dcc.Dropdown(
            id='x_attribute',
            options=[{'label': attribute, 'value': attribute} for attribute in ATTRIBUTES],
            value=ATTRIBUTES[0]
        ),

        # Dropdown menu for selecting the y attribute
        html.Label('Select Y Attribute:'),
        dcc.Dropdown(
            id='y_attribute',
            options=[{'label': attribute, 'value': attribute} for attribute in ATTRIBUTES],
            value=ATTRIBUTES[1]
        )
    ], style={'width': '80%', 'margin': 'auto'}),

    # The graph itself
    dcc.Graph(id='scatterplot', style={'height': '80vh'})
])


# Define a callback function for updating the graph
@app.callback(
    Output('scatterplot', 'figure'),
    [Input('event', 'value'),
     Input('x_attribute', 'value'),
     Input('y_attribute', 'value')]
)
def update_graph(event, x_attribute, y_attribute):
    # Filter the data based on the selected event
    if event != 'all':
        filtered_df = df[df['Event'] == event]
        title = f'Scatterplot of {x_attribute} vs {y_attribute} for {event} Events'
    else:
        filtered_df = df
        title = f'Scatterplot of {x_attribute} vs {y_attribute} for All Events'
    filtered_df['Cluster'] = filtered_df['Cluster'].astype(str)
    # Create a scatterplot for the selected attributes
    fig = px.scatter(filtered_df, x=x_attribute, y=y_attribute, color='Cluster',
                     color_discrete_sequence=px.colors.qualitative.Set1, hover_name='Event', title=title)
    fig.update_layout(title_x=0.5, xaxis_title=x_attribute, yaxis_title=y_attribute)

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()