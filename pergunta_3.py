import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import numpy as np

# Load the data
df = pd.read_csv("data/polished3_with_gdp.csv")
ATTRIBUTES = ["Height", "BMI", "Age", "GDP"]

# Add gender options for the dropdown
gender_options = [{"label": "Male", "value": "M"}, {"label": "Female", "value": "F"}]

def process(dataframe):
    grouped = dataframe.groupby(['Event', 'Sport'])[ATTRIBUTES].mean().reset_index()
    scaler = StandardScaler()
    grouped[ATTRIBUTES] = scaler.fit_transform(grouped[ATTRIBUTES])
    return grouped

def adjust_medals(dataframe, medal_multiplier=2):
    copies = dataframe[dataframe['Won Medal'] == True].copy()
    for _ in range(medal_multiplier - 2):
        copies = pd.concat([copies, dataframe[dataframe['Won Medal'] == True]])
    df_with_copies = pd.concat([dataframe, copies], ignore_index=True)
    return df_with_copies

def recalculate_coords(dataframe, attributes, method='MDS', medal_multiplier=2):
    df_with_copies = adjust_medals(dataframe, medal_multiplier=medal_multiplier)
    df_with_copies = process(df_with_copies)
    scaler = MinMaxScaler()
    feature_data = df_with_copies[attributes].reset_index(drop=True)
    scaled_feature_data = scaler.fit_transform(feature_data)
    feature_data = pd.DataFrame(scaled_feature_data, columns=feature_data.columns)

    if method == 'MDS':
        reducer = MDS(n_components=3, dissimilarity='euclidean', random_state=42)
        coords = reducer.fit_transform(feature_data)
        stress = reducer.stress_
    elif method == 'PCA':
        reducer = PCA(n_components=3)
        coords = reducer.fit_transform(feature_data)
        stress = None

    return_df = pd.DataFrame(coords, columns=['x', 'y', 'z'], index=df_with_copies.index)
    return pd.concat([df_with_copies, return_df], axis=1), stress

# Get the unique list of events and sports for the dropdowns
event_options = [{"label": event, "value": event} for event in df["Event"].unique()]
sport_options = [{"label": sport, "value": sport} for sport in df["Sport"].unique()]

#app = dash.Dash(__name__)

layout = html.Div([
    # Botão para mostrar/ocultar o menu
    html.Div([
        dbc.Button('Mostrar/Ocultar Menu', id='toggle-menu-button', n_clicks=0, color='primary', style={
            'margin': '10px',
            'padding': '10px 20px',
            'fontSize': '16px',
            'fontFamily': 'Arial, sans-serif',
            'borderRadius': '5px',
            'cursor': 'pointer'
        })
    ], style={'textAlign': 'center'}),
    
    # Menu Superior (colapsável)
    dbc.Collapse(
        id='menu-collapse',
        is_open=True,
        children=[
            html.Div([
                # Título do Dashboard
                html.H1("Sport Similarity", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'fontFamily': 'Arial, sans-serif',
                'color': '#333',
                'marginTop': '20px'
            }),

            # Linha 1: Select a Gender e Select a Sport
            html.Div([
                html.Div([
                    html.Label("Select Gender:", style={'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='gender-selector',
                        options=[{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}],
                        value='M',
                        style={'width': '100%', 'marginBottom': '20px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

                html.Div([
                    html.Label("Select a Sport:", style={'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='sport-selector',
                        options=sport_options,
                        placeholder="Select a Sport",
                        style={'width': '100%', 'marginBottom': '20px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Linha 2: Select an Event e Select Features
            html.Div([
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
                        value=ATTRIBUTES,
                        style={'width': '100%', 'marginBottom': '20px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Linha 3: Medal Multiplier e Select Dimensionality Reduction Method
            html.Div([
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
                        value="MDS",
                        style={'width': '100%', 'marginBottom': '20px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            # View Selector - Centralizado
            html.Div([
        dcc.Checklist(
            id='view-selector',
            options=[{'label': '3D View', 'value': '3D'}],
            value=['2D'],
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        )
    ], style={'width': '48%', 'margin': '0 auto', 'marginBottom': '20px', 'textAlign': 'center'}),

], style={
                'padding': '20px',
                'backgroundColor': '#f0f0f0',
                'borderRadius': '10px',
                'marginBottom': '20px'
            }),
        ]
    ),

    # Scatter Plot
    dcc.Graph(id='scatter-plot'),

    # Stress Metric
    html.Div(id='stress-metric', style={'textAlign': 'center', 'marginTop': '20px'})
    
], style={'width': '80%', 'margin': '0 auto'})


def register_callbacks(app):
    @app.callback(
        [Output('event-selector', 'options'),  # Dynamic event options based on gender
         Output('scatter-plot', 'figure'),
         Output('stress-metric', 'children')],
        [Input('gender-selector', 'value'),  # Gender selection input
         Input('sport-selector', 'value'),  # Sport selection input
         Input('event-selector', 'value'),  # Event selection input
         Input('attribute-selector', 'value'),  # Feature selection input
         Input('medal-multiplier-input', 'value'),  # Medal multiplier input
         Input('method-selector', 'value'),  # MDS or PCA selection
         Input('view-selector', 'value')]  # 2D or 3D view selection
    )
    def update_graph(selected_gender, selected_sport, selected_event, selected_attributes, medal_multiplier,
                     selected_method, view_selector):
        # Filter the events based on selected gender
        filtered_df = df[df["Sex"] == selected_gender]  # Filter by selected gender

        # Generate the event options based on the filtered dataframe
        event_options = [{"label": event, "value": event} for event in filtered_df["Event"].unique()]

        # Recalculate coordinates based on the filtered dataframe
        recalculated_coords, stress = recalculate_coords(filtered_df, selected_attributes, selected_method,
                                                         medal_multiplier)

        if '3D' in view_selector:
            fig = px.scatter_3d(
                recalculated_coords,
                x='x',
                y='y',
                z='z',
                hover_data=['Event', 'Sport'] + selected_attributes,
                title="Dimensionality Reduction Plot (3D)"
            )
            fig.update_layout(
                scene=dict(xaxis_title='X Coordinate', yaxis_title='Y Coordinate', zaxis_title='Z Coordinate'),
                hovermode='closest',
                title={'text': f"{selected_method} Plot of Bio By Sport {selected_gender} (3D)", 'x': 0.5,
                       'xanchor': 'center'})
        else:
            fig = px.scatter(
                recalculated_coords,
                x='x',
                y='y',
                hover_data=['Event', 'Sport'] + selected_attributes,
                title="Dimensionality Reduction Plot (2D)"
            )
            fig.update_layout(xaxis_title='X Coordinate', yaxis_title='Y Coordinate', hovermode='closest',
                              title={'text': f"{selected_method} Plot of Bio By Sport {selected_gender} (2D)", 'x': 0.5,
                                     'xanchor': 'center'})

        if selected_sport or selected_event:
            fig.update_traces(
                marker=dict(
                    color=["green" if sport == selected_sport else ("red" if event == selected_event else "blue")
                           for sport, event in zip(recalculated_coords["Sport"], recalculated_coords["Event"])],
                    size=[14 if sport == selected_sport else (12 if event == selected_event else 8)
                          for sport, event in zip(recalculated_coords["Sport"], recalculated_coords["Event"])])
            )

        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Sport: %{customdata[1]}<br>" +
                          "<br>".join(
                              [f"{attr}: %{{customdata[{i + 2}]}}" for i, attr in enumerate(selected_attributes)])
        )

        stress_message = f"Stress value for MDS: {stress:.4f}" if selected_method == 'MDS' else "PCA does not calculate stress."

        return event_options, fig, stress_message

# Run the app
#if __name__ == '__main__':
    #app.run_server(debug=True)
