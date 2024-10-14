# Import necessary libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from scipy import stats
from sklearn.preprocessing import StandardScaler

COLUMNS = ["Height", "Age", "BMI"]

# Load the data from the csv file
df = pd.read_csv('athlete_data.csv')
df = df[COLUMNS]
scaler = StandardScaler()
normalized_data = scaler.fit_transform(df)
df = pd.DataFrame(normalized_data, columns=df.columns)

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1('Olympic Athletes Dashboard', style={'textAlign': 'center'}),
    html.P('Select one or more features to see their distributions:', style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='feature-dropdown',
            options=[{'label': feature, 'value': feature} for feature in df.columns],
            value=[df.columns[0]],
            multi=True
        )
    ], style={'width': '50%', 'margin': 'auto'}),
    html.P('Note: You can select multiple features by holding the Ctrl key while clicking.',
           style={'textAlign': 'center', 'fontSize': '12px', 'color': 'gray'}),
    dcc.Graph(id='distribution-graph'),
    html.Div(id='stats-output', style={'textAlign': 'center'})
], style={'padding': '20px'})


# Define a callback function to update the graph
@app.callback(
    [Output('distribution-graph', 'figure'),
     Output('stats-output', 'children')],
    [Input('feature-dropdown', 'value')]
)
def update_graph(selected_features):
    # Melt the dataframe to create a single column for the values
    data_to_plot = [df[feature] for feature in selected_features]

    # Create a histogram figure using Plotly Express
    melted_df = df[selected_features].melt(var_name='Feature', value_name='Value')

    # Create a density plot using Plotly Express
    fig = px.histogram(
        melted_df,
        x='Value',
        color='Feature',
        barmode='overlay',
        histnorm='density',  # Normalize to show density
        title='Distributions of Selected Features',
        nbins=50
    )
    # Calculate the statistics
    stats_output = []
    for feature in selected_features:
        mean = df[feature].mean()
        std = df[feature].std()
        kurtosis = stats.kurtosis(df[feature])
        stats_output.append(html.P(f'{feature}: mean = {mean:.2f}, std = {std:.2f}, kurtosis = {kurtosis:.2f}'))

    return fig, stats_output


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)