import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import kurtosis, entropy
from dash import dash_table

from utils import adjust_medals

# Load the dataset
df = pd.read_csv('data/polished3_with_gdp.csv')

ATTRIBUTES = ["Height", "BMI", "Age", "GDP"]
columns_to_normalize = ATTRIBUTES

# Standardize the data
scaler = StandardScaler()

male = df[df["Sex"] == "M"]
female = df[df["Sex"] == "F"]

male.loc[:, columns_to_normalize] = scaler.fit_transform(male[columns_to_normalize])
female.loc[:, columns_to_normalize] = scaler.fit_transform(female[columns_to_normalize])

df = pd.concat([male, female])

# Unique events and features for dropdowns
unique_events = df['Event'].unique()
unique_features = columns_to_normalize

def create_page_site2(app):
    layout = html.Div([
        # Event selector (allow multiple selections)
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

        dcc.Dropdown(
            id='event-selector',
            options=[{'label': event, 'value': event} for event in unique_events],
            value=[unique_events[0]],  # Default first event selected
            multi=True,
            clearable=False
        ),

        # Feature selector (allow multiple selections)
        dcc.Dropdown(
            id='feature-selector',
            options=[{'label': feature, 'value': feature} for feature in unique_features],
            value=unique_features,  # Default all features selected
            multi=True,
            clearable=False
        ),

        # Table for kurtosis and entropy
        dash_table.DataTable(
            id='stats-table',
            columns=[
                {"name": "Event", "id": "event"},
                {"name": "Kurtosis", "id": "kurtosis"},
                {"name": "Entropy", "id": "entropy"}
            ],
            data=[]
        ),

        # Display KDE plots
        dcc.Graph(id='kde-plot')
    ])


    @app.callback(
        [Output('stats-table', 'data'),
        Output('kde-plot', 'figure')],
        [Input('event-selector', 'value'),
        Input('feature-selector', 'value'),
        Input('medal-multiplier-input', 'value')]
    )
    def update_dashboard(selected_events, selected_features, mm):
        adjusted_df = adjust_medals(df, mm)

        # Prepare the table data for kurtosis and entropy
        stats_data = []

        # Prepare KDE data
        kde_data = []
        kde_labels = []

        # Handle multiple events
        if len(selected_events) > 1:
            for event in selected_events:
                # Filter data for the current event
                df_event = adjusted_df[adjusted_df['Event'] == event][selected_features]

                # Apply PCA for dimensionality reduction
                pca = PCA(n_components=1)
                transformed = pca.fit_transform(df_event)

                # Calculate kurtosis and entropy for PCA-transformed data
                kurt = kurtosis(transformed.squeeze())
                ent = entropy(np.histogram(transformed.squeeze(), bins=10)[0])

                # Append stats to the table
                stats_data.append({
                    "event": event,
                    "kurtosis": f"{kurt:.2f}",
                    "entropy": f"{ent:.2f}"
                })

                # Add data for KDE plot
                kde_data.append(transformed.squeeze())
                kde_labels.append(f'{event} (PCA)')

            # Create a combined KDE plot for all events
            kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)

        else:
            # If only one event is selected, calculate kurtosis and entropy for each feature
            df_event = df[df['Event'].isin(selected_events)][selected_features]
            event = selected_events[0]

            for feature in selected_features:
                # Calculate kurtosis and entropy for each feature
                feature_data = df_event[feature]
                kurt = kurtosis(feature_data)
                ent = entropy(np.histogram(feature_data, bins=10)[0])

                # Append stats to the table
                stats_data.append({
                    "event": f'{event} - {feature}',
                    "kurtosis": f"{kurt:.2f}",
                    "entropy": f"{ent:.2f}"
                })

                # Add data for KDE plot
                kde_data.append(feature_data)
                kde_labels.append(feature)

            # Create a KDE plot for each feature
            kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)

        return stats_data, kde_fig

    return layout
