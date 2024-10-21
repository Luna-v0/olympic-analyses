import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler, MinMaxScaler

base_file_path = '../../data/'

# Load the data
df = pd.read_csv(base_file_path+"polished3_with_gdp.csv")
df = df[df["Sex"] == "M"]
ATTRIBUTES = ["Height", "BMI", "Age", "GDP"]

def process(dataframe):
    grouped = dataframe.groupby(['Event', 'Sport'])[ATTRIBUTES].mean().reset_index()
    scaler = StandardScaler()
    grouped[ATTRIBUTES] = scaler.fit_transform(grouped[ATTRIBUTES])
    return grouped

def recalculate_coords(dataframe, attributes, method='MDS', medal_multiplier=2):
    copies = dataframe[dataframe['Won Medal'] == True].copy()

    # Use pd.concat to create n copies
    for _ in range(medal_multiplier - 2):  # we already have 1 copy
        copies = pd.concat([copies, dataframe[dataframe['Won Medal'] == True]])

    # Concatenate original DataFrame with the new copies
    df_with_copies = pd.concat([dataframe, copies], ignore_index=True)
    df_with_copies = process(df_with_copies)

    # Ensure that only the selected attributes are used
    scaler = MinMaxScaler()
    feature_data = df_with_copies[attributes].reset_index(drop=True)
    scaled_feature_data = scaler.fit_transform(feature_data)
    feature_data = pd.DataFrame(scaled_feature_data, columns=feature_data.columns)

    # Apply MDS or PCA based on user's selection
    if method == 'MDS':
        reducer = MDS(n_components=2, dissimilarity='euclidean', random_state=42)
        coords = reducer.fit_transform(feature_data)
        stress = reducer.stress_  # Only for MDS
    elif method == 'PCA':
        reducer = PCA(n_components=2)
        coords = reducer.fit_transform(feature_data)
        stress = None  # PCA does not have a stress metric

    return_df = pd.DataFrame(coords, columns=['x', 'y'], index=df_with_copies.index)
    return pd.concat([df_with_copies, return_df], axis=1), stress

# Get the unique list of events for the dropdown
event_options = [{"label": event, "value": event} for event in df["Event"].unique()]
sport_options = [{"label": sport, "value": sport} for sport in df["Sport"].unique()]

app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Sport Similarity", style={'textAlign': 'center', 'marginBottom': '30px'}),

    html.Div([
        html.Label("Select a Sport:", style={'marginBottom': '5px'}),
        dcc.Dropdown(
            id='sport-selector',
            options=sport_options,
            placeholder="Select a Sport",
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

    html.Div([
        html.Label("Select an Event:", style={'marginBottom': '5px'}),
        dcc.Dropdown(
            id='event-selector',
            options=event_options,
            placeholder="Select an Event",
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

    html.Div([
        html.Label("Select Features:", style={'marginBottom': '5px'}),
        dcc.Dropdown(
            id='attribute-selector',
            options=[{"label": attr, "value": attr} for attr in ATTRIBUTES],
            multi=True,
            value=ATTRIBUTES,  # Default to using all attributes
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '100%', 'padding': '0 10px'}),

    html.Div([
        html.Label("Medal Multiplier:", style={'marginBottom': '5px'}),
        dcc.Input(
            id='medal-multiplier-input',
            type='number',
            value=2,
            min=1,
            step=1,
            placeholder="Medal Multiplier",
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

    html.Div([
        html.Label("Select Dimensionality Reduction Method:", style={'marginBottom': '5px'}),
        dcc.Dropdown(
            id='method-selector',
            options=[{"label": "MDS", "value": "MDS"},
                     {"label": "PCA", "value": "PCA"}],
            value="MDS",  # Default method
            style={'width': '100%', 'marginBottom': '20px'}
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

    dcc.Graph(id='scatter-plot'),

    html.Div(id='stress-metric', style={'textAlign': 'center', 'marginTop': '20px'})
], style={'width': '80%', 'margin': '0 auto'})

# Callback to update the graph
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('stress-metric', 'children')],
    [Input('sport-selector', 'value'),  # Sport selection input
     Input('event-selector', 'value'),  # Event selection input
     Input('attribute-selector', 'value'),  # Feature selection input
     Input('medal-multiplier-input', 'value'),  # Medal multiplier input
     Input('method-selector', 'value')]  # MDS or PCA selection
)
def update_graph(selected_sport, selected_event, selected_attributes, medal_multiplier, selected_method):
    recalculated_coords, stress = recalculate_coords(df, selected_attributes, selected_method, medal_multiplier)

    fig = px.scatter(
        recalculated_coords,
        x='x',  # x coordinates
        y='y',  # y coordinates
        hover_data=['Event', 'Sport'] + selected_attributes,
        title="Dimensionality Reduction Plot"
    )

    if selected_sport or selected_event:
        fig.update_traces(
            marker=dict(color=[
                "green" if sport == selected_sport else (
                    "red" if event == selected_event else "blue")
                for sport, event in zip(recalculated_coords["Sport"], recalculated_coords["Event"])
            ],
                size=[
                    14 if sport == selected_sport else (
                        12 if event == selected_event else 8)
                    for sport, event in zip(recalculated_coords["Sport"], recalculated_coords["Event"])
                ])
        )

    fig.update_layout(
        xaxis_title='X Coordinate',
        yaxis_title='Y Coordinate',
        hovermode='closest',
        title={'text': f"{selected_method} Plot of Bio By Sport Male", 'x': 0.5, 'xanchor': 'center'}
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Sport: %{customdata[1]}<br>" +
                      "<br>".join([f"{attr}: %{{customdata[{i+2}]}}" for i, attr in enumerate(selected_attributes)])
    )

    if selected_method == 'MDS':
        stress_message = f"Stress value for MDS: {stress:.4f}"
    else:
        stress_message = "PCA does not calculate stress."

    return fig, stress_message


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
