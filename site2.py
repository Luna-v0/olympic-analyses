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
unique_sports = df['Sport'].unique()
unique_events = df['Event'].unique()
unique_features = columns_to_normalize

def create_page_site2(app):
    layout = html.Div([
        dcc.RadioItems(
            id='filter-type',
            options=[
                {'label': 'Sport', 'value': 'Sport'},
                {'label': 'Event', 'value': 'Event'}
            ],
            value='Event',
            inline=True,
            style={'marginBottom': '10px'}
        ),
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
            id='event-sport-selector',
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
                {"name": "Event/Sport", "id": "event_sport"},
                {"name": "Kurtosis", "id": "kurtosis"},
                {"name": "Entropy", "id": "entropy"}
            ],
            data=[]
        ),

        # Display KDE plots
        dcc.Graph(id='kde-plot')
    ])
    
    @app.callback(
    [Output('event-sport-selector', 'options'),
     Output('event-sport-selector', 'value')],
    [Input('filter-type', 'value')]
    )
    def update_selector_options(filter_type):
        if filter_type == 'Event':
            options = [{'label': event, 'value': event} for event in unique_events]
            return options, [unique_events[0]]  # Default first event selected
        else:
            options = [{'label': sport, 'value': sport} for sport in unique_sports]
            return options, [unique_sports[0]]  # Default first sport selected


    @app.callback(
        [Output('stats-table', 'data'),
        Output('kde-plot', 'figure')],
        [Input('event-sport-selector', 'value'),
        Input('feature-selector', 'value'),
        Input('medal-multiplier-input', 'value')]
    )
    def update_dashboard(selected_values, selected_features, mm, filter_type):
        adjusted_df = adjust_medals(df, mm)

        # Prepare the table data for kurtosis and entropy
        stats_data = []

        # Prepare KDE data
        kde_data = []
        kde_labels = []

        # Handle multiple events
        if len(selected_values) > 1:
            for value in selected_values:
                # Filter data based on the selected filter type
                if filter_type == 'Event':
                    df_filtered = adjusted_df[adjusted_df['Event'] == value][selected_features]
                else:
                    df_filtered = adjusted_df[adjusted_df['Sport'] == value][selected_features]

                # Apply PCA for dimensionality reduction
                pca = PCA(n_components=1)
                transformed = pca.fit_transform(df_filtered)

                # Calculate kurtosis and entropy for PCA-transformed data
                kurt = kurtosis(transformed.squeeze())
                ent = entropy(np.histogram(transformed.squeeze(), bins=10)[0])

                # Append stats to the table
                stats_data.append({
                    "event_sport": value,
                    "kurtosis": f"{kurt:.2f}",
                    "entropy": f"{ent:.2f}"
                })

                # Add data for KDE plot
                kde_data.append(transformed.squeeze())
                kde_labels.append(f'{value} (PCA)')

            # Create a combined KDE plot for all events
            kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)

        else:
            # If only one event is selected, calculate kurtosis and entropy for each feature
            if filter_type == 'Event':
                df_filtered = adjusted_df[adjusted_df['Event'].isin(selected_values)][selected_features]
            else:
                df_filtered = adjusted_df[adjusted_df['Sport'].isin(selected_values)][selected_features]
                
            value = selected_values[0]

            for feature in selected_features:
                # Calculate kurtosis and entropy for each feature
                feature_data = df_filtered[feature]
                kurt = kurtosis(feature_data)
                ent = entropy(np.histogram(feature_data, bins=10)[0])

                # Append stats to the table
                stats_data.append({
                    "event_sport": f'{value} - {feature}',
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
