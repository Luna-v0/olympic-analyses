import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import kurtosis

df = pd.read_csv('data/polished3_with_gdp.csv')

male = df[df["Sex"] == "M"]
female = df[df["Sex"] == "F"]

columns_to_normalize = ["Height", "BMI", "Age", "GDP"]

used_columns = columns_to_normalize + ["Event"]

scaler = StandardScaler()

male.loc[:, columns_to_normalize] = scaler.fit_transform(male[columns_to_normalize])
female.loc[:, columns_to_normalize] = scaler.fit_transform(female[columns_to_normalize])

df = pd.concat([male, female])[used_columns]

app = dash.Dash(__name__)

# Dropdown options for events
unique_events = df['Event'].unique()

app.layout = html.Div([
    # Event selector
    dcc.Dropdown(
        id='event-selector',
        options=[{'label': event, 'value': event} for event in unique_events],
        value=unique_events[0],  # Default selected event
        clearable=False
    ),

    # PCA toggle
    dcc.RadioItems(
        id='pca-toggle',
        options=[
            {'label': 'Use PCA', 'value': 'pca'},
            {'label': 'No PCA', 'value': 'no_pca'}
        ],
        value='no_pca',
        labelStyle={'display': 'inline-block'}
    ),

    # Display kurtosis for both male and female
    html.Div(dangerously_allow_html=True, id='kurtosis-output'),

    # Display KDE plots
    dcc.Graph(id='kde-plot')
])


@app.callback(
    [Output('kurtosis-output', 'children'),
     Output('kde-plot', 'figure')],
    [Input('event-selector', 'value'),
     Input('pca-toggle', 'value')]
)
def update_dashboard(selected_event, pca_option):
    # Filter data for the selected event
    df_event = df[df['Event'] == selected_event][used_columns]


    # Apply PCA if selected
    if pca_option == 'pca':
        # Apply PCA
        pca = PCA(n_components=1)
        transformed = pca.fit_transform(df_event)

        # Calculate kurtosis for the PCA-transformed data
        kurt = kurtosis(transformed.squeeze())

        # Use PCA-transformed data for KDE plots
        kde_data = transformed.squeeze()
        kde_labels = 'PCA'

        # Display single kurtosis value for PCA
        kurtosis_text = f"<b>Kurtosis for {selected_event} (PCA): {kurt:.2f}</b><br>"

    else:
        # Calculate kurtosis for each feature when PCA is not used
        kurt = {col: kurtosis(df_event[col]) for col in columns_to_normalize}

        # Use original normalized data for KDE plots
        kde_data = [df_event[col] for col in columns_to_normalize]
        kde_labels = [f'{col}' for col in columns_to_normalize]

        # Display kurtosis for each feature
        kurtosis_text = f"<b>Kurtosis for {selected_event}:</b><ul>"
        for col in columns_to_normalize:
            kurtosis_text += f"<li>{col}: {kurt[col]:.2f}</li>"
        kurtosis_text += "</ul>"

    # KDE plot
    kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)

    return kurtosis_text, kde_fig


if __name__ == '__main__':
    app.run_server(debug=True)
