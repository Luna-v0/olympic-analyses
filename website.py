# Import necessary libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

# Load the data from CSV files
df_male = pd.read_csv('bio_by_sport_male.csv')
df_female = pd.read_csv('bio_by_sport_female.csv')

# Define the constants
ATTRIBUTES = df_male.columns.drop(['Event']).tolist()
TITLE = 'Olympics Data Scatterplot'
MAX_CLUSTERS = 6

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1(TITLE, style={'textAlign': 'center', 'margin': '20px'}),

    # Gender, Attributes, and Cluster selection
    html.Div([
        # Gender selection (label + dropdown aligned)
        html.Div([
            html.Label('Select Gender:', style={'marginRight': '10px', 'alignSelf': 'center'}),
            dcc.Dropdown(
                id='gender',
                options=[{'label': 'Male', 'value': 'male'}, {'label': 'Female', 'value': 'female'}],
                value='male',
                style={'width': '200px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '10px'}),

        # Attribute selection (label + dropdown aligned)
        html.Div([
            html.Label('Select Attributes:', style={'marginRight': '10px', 'alignSelf': 'center'}),
            dcc.Dropdown(
                id='attributes',
                options=[{'label': attribute, 'value': attribute} for attribute in ATTRIBUTES],
                value=ATTRIBUTES[:2],
                multi=True,
                style={'width': '400px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '10px'}),

        # Cluster number selection (label + dropdown aligned)
        html.Div([
            html.Label('Select Number of Clusters:', style={'marginRight': '10px', 'alignSelf': 'center'}),
            dcc.Dropdown(
                id='num_clusters',
                options=[{'label': i, 'value': i} for i in range(2, MAX_CLUSTERS + 1)],
                value=2,
                style={'width': '200px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '10px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'margin': '20px'}),

    # Graph and Metrics Container
    html.Div([
        # The graph on the left
        dcc.Graph(id='scatterplot', style={'width': '70%', 'display': 'inline-block', 'height': '80vh', 'margin': '20px'}),

        # Clustering metrics on the right
        html.Div([
            html.H2('Clustering Metrics', style={'margin': '10px'}),
            html.Div(id='metrics-container', style={'margin': '20px'})  # Container for metrics display
        ], style={'width': '28%', 'display': 'inline-block', 'verticalAlign': 'top', 'margin': '20px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '100%', 'margin': 'auto', 'overflow': 'auto'})
], style={'backgroundColor': '#f2f2f2', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})

# Define a callback function for updating the graph and metrics
@app.callback(
    [Output('scatterplot', 'figure'),
     Output('metrics-container', 'children')],
    [Input('gender', 'value'),
     Input('attributes', 'value'),
     Input('num_clusters', 'value')]
)
def update_graph(gender, attributes, num_clusters):
    # Select the DataFrame based on the gender
    if gender == 'male':
        df = df_male
    else:
        df = df_female

    # Check if there are enough attributes for PCA
    if len(attributes) < 3:
        return {'data': [], 'layout': {'title': 'Please select at least 2 attributes'}}, html.P("")

    # Create a new DataFrame with the selected attributes
    pca_df = df.loc[:, attributes + ['Event']]

    # Apply PCA if there are more than 2 attributes
    if len(attributes) > 3:
        pca = PCA(n_components=3)
        scaler = StandardScaler()
        pca_values = pca.fit_transform(scaler.fit_transform(pca_df[attributes]))
        pca_df['Principal Component 1'] = pca_values[:, 0]
        pca_df['Principal Component 2'] = pca_values[:, 1]
        pca_df['Principal Component 3'] = pca_values[:, 2]

        # Create a scatterplot for the selected attributes
        title = 'Scatterplot of Principal Components'
        cluster_df = pca_df[['Principal Component 1', 'Principal Component 2']]
    else:
        # Create a scatterplot for the selected attributes without PCA
        title = f'Scatterplot of {attributes[0]} vs {attributes[1]}'
        cluster_df = pca_df[attributes]

    # Calculate the clusters
    kmeans = KMeans(n_clusters=num_clusters)
    pca_df['Cluster'] = kmeans.fit_predict(cluster_df)
    pca_df['Cluster'] = pca_df['Cluster'].astype('category')

    # Create a scatterplot for the selected attributes
    hover_name = 'Event'
    hover_data = attributes
    fig = px.scatter_3d(pca_df, 
                    x=cluster_df.columns[0], 
                    y=cluster_df.columns[1], 
                    z=cluster_df.columns[2] if len(cluster_df.columns) > 2 else 'Dummy Z',  # Adding the third dimension for 3D plot
                    color='Cluster',
                    color_discrete_sequence=px.colors.qualitative.Set1, 
                    hover_name=hover_name, 
                    hover_data=hover_data, 
                    title=title)

    fig.update_layout(title_x=0.5, 
                  scene=dict(
                      xaxis_title=cluster_df.columns[0],
                      yaxis_title=cluster_df.columns[1],
                      zaxis_title=cluster_df.columns[2]  if len(cluster_df.columns) > 2 else 'Dummy Z'
                  ))

    # Calculate the silhouette score
    score = silhouette_score(cluster_df, pca_df['Cluster'])

    # Group the metrics in a container
    metrics = html.Div([
        html.P(f'Silhouette Score: {score:.2f}', style={'fontSize': '16px', 'fontWeight': 'bold'}),
        html.P(f'Number of Clusters: {num_clusters}', style={'fontSize': '16px', 'fontWeight': 'bold'})
    ])

    return fig, metrics


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)