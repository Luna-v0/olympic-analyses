import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import kurtosis, entropy
#from app import app

# Certifique-se de que este módulo está disponível corretamente
from pergunta_3 import adjust_medals

# Carregar o dataset
df = pd.read_csv('data/polished3_with_gdp.csv')

# Definir atributos e colunas para normalização
ATTRIBUTES = ["Height", "BMI", "Age", "GDP"]
columns_to_normalize = ATTRIBUTES

# Listas únicas para dropdowns
unique_features = columns_to_normalize

# Inicializar o aplicativo Dash com estilos Bootstrap
#external_stylesheets = [dbc.themes.BOOTSTRAP]
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

print("Loading pergunta_1 layout...")
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
                html.H1("Análise Olímpica", style={
                    'textAlign': 'center',
                    'marginBottom': '20px',
                    'fontFamily': 'Arial, sans-serif',
                    'color': '#333',
                    'marginTop': '20px'
                }),

                # Linha 1: Filter Type, Gender Selector e Medal Multiplier
                html.Div([
                    # Filter Type
                    html.Div([
                        html.Label('Filtrar por:', style={'marginRight': '10px', 'fontWeight': 'bold'}),
                        dcc.RadioItems(
                            id='filter-type',
                            options=[
                                {'label': ' Evento', 'value': 'Event'},
                                {'label': ' Esporte', 'value': 'Sport'}
                            ],
                            value='Event',  # Filtro padrão por Evento
                            inline=True,
                            labelStyle={'marginRight': '15px', 'fontFamily': 'Arial, sans-serif', 'color': '#333'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '30px'}),

                    # Gender Selector
                    html.Div([
                        html.Label('Gênero:', style={'marginRight': '10px', 'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='gender-selector',
                            options=[
                                {'label': 'Masculino', 'value': 'M'},
                                {'label': 'Feminino', 'value': 'F'}
                            ],
                            value='M',
                            clearable=False,
                            style={'width': '150px', 'fontFamily': 'Arial, sans-serif', 'color': '#333'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '30px'}),

                    # Medal Multiplier
                    html.Div([
                        html.Label("Medal Multiplier:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
                        dcc.Input(
                            id='medal-multiplier-input',
                            type='number',
                            value=2,
                            min=1,
                            step=1,
                            placeholder="Medal Multiplier",
                            style={
                                'width': '150px',
                                'padding': '5px',
                                'border': '1px solid #ccc',
                                'borderRadius': '4px',
                                'fontFamily': 'Arial, sans-serif',
                                'color': '#333'
                            }
                        )
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'}),

                # Linha 2: Event/Sport Selector e Feature Selector
                html.Div([
                    # Event/Sport Selector
                    html.Div([
                        html.Label(id='event-sport-label', style={'marginBottom': '5px', 'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='event-sport-selector',
                            value=[],  # Valor padrão vazio
                            multi=True,
                            clearable=False,
                            style={
                                'width': '100%',
                                'fontFamily': 'Arial, sans-serif',
                                'color': '#333',
                                'maxHeight': '200px',  # Altura máxima do dropdown
                            }
                        )
                    ], style={'flex': '1', 'marginRight': '20px'}),

                    # Feature Selector
                    html.Div([
                        html.Label('Selecione os Atributos:', style={'marginBottom': '5px', 'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='feature-selector',
                            options=[{'label': feature, 'value': feature} for feature in unique_features],
                            value=unique_features,  # Todos os atributos selecionados por padrão
                            multi=True,
                            clearable=False,
                            style={'width': '100%', 'fontFamily': 'Arial, sans-serif', 'color': '#333'}
                        )
                    ], style={'flex': '1'}),
                ], style={'display': 'flex', 'marginBottom': '20px'}),
            ], style={
                'padding': '20px',
                'backgroundColor': '#f0f0f0',
                'borderRadius': '10px',
                'marginBottom': '20px'
            }),
        ]
    ),

    # Divisão para o gráfico e a tabela de eventos mais próximos
    html.Div([
        # Gráfico KDE
        html.Div([
            dcc.Graph(id='kde-plot', style={'height': '500px'})
        ], style={'flex': '2', 'marginRight': '20px'}),

    ], style={
        'display': 'flex',
        'marginBottom': '20px',
        'padding': '20px',
        'backgroundColor': '#ffffff',
        'borderRadius': '10px',
        'alignItems': 'flex-start'
    }),

    # Tabela para exibir kurtosis e entropia
    html.Div([
        dash_table.DataTable(
            id='stats-table',
            columns=[
                {"name": "", "id": "event_sport"},
                {"name": "Kurtosis", "id": "kurtosis"},
                {"name": "Entropia", "id": "entropy"}
            ],
            data=[],
            style_table={
                'marginBottom': '20px',
                'overflowX': 'auto'
            },
            style_cell={
                'textAlign': 'left',
                'fontFamily': 'Arial, sans-serif',
                'color': '#333',
                'padding': '5px'
            },
            style_header={
                'backgroundColor': '#f1f1f1',
                'fontWeight': 'bold'
            },
        )
    ], style={
        'padding': '20px',
        'backgroundColor': '#ffffff',
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),
], style={
    'maxWidth': '1200px',
    'margin': '0 auto',
    'backgroundColor': '#e5e5e5',
    'padding': '0 20px'
})

def register_callbacks(app):
    # Callback para controlar o colapso do menu
    @app.callback(
        Output('menu-collapse', 'is_open'),
        [Input('toggle-menu-button', 'n_clicks')],
        [State('menu-collapse', 'is_open')]
    )
    def toggle_menu(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Atualizar opções do seletor de Evento/Esporte com base no gênero e tipo de filtro
    @app.callback(
        [Output('event-sport-selector', 'options'),
        Output('event-sport-selector', 'value'),
        Output('event-sport-label', 'children')],
        [Input('filter-type', 'value'),
        Input('gender-selector', 'value')]
    )
    def update_selector_options(filter_type, gender):
        df_gender = df[df['Sex'] == gender]
        if filter_type == 'Event':
            options = [{'label': event, 'value': event} for event in sorted(df_gender['Event'].unique())]
            label = 'Selecione o(s) Evento(s):'
            default_value = [options[0]['value']] if options else []
            return options, default_value, label
        else:
            options = [{'label': sport, 'value': sport} for sport in sorted(df_gender['Sport'].unique())]
            label = 'Selecione o(s) Esporte(s):'
            default_value = [options[0]['value']] if options else []
            return options, default_value, label

    # Atualizar tabela, gráfico e tabela de eventos próximos
    @app.callback(
        [Output('stats-table', 'data'),
        Output('kde-plot', 'figure'),
        Output('stats-table', 'columns')],
        [Input('event-sport-selector', 'value'),
        Input('feature-selector', 'value'),
        Input('medal-multiplier-input', 'value'),
        Input('filter-type', 'value'),
        Input('gender-selector', 'value')]
    )
    def update_dashboard(selected_values, selected_features, mm, filter_type, gender):
        if not selected_values:
            return [], {}, [], [], [], ''

        df_gender = df[df['Sex'] == gender]

        adjusted_df = adjust_medals(df_gender, mm)

        # Verificar se o adjust_medals retornou dados
        if adjusted_df.empty:
            return [], {}, [], [], [], ''

        # Normalizar os dados
        scaler = StandardScaler()
        adjusted_df[selected_features] = scaler.fit_transform(adjusted_df[selected_features])

        # Dados para a tabela de estatísticas
        stats_data = []

        # Dados para o gráfico KDE
        kde_data = []
        kde_labels = []

        # Atualizar colunas das tabelas dinamicamente
        if filter_type == 'Event':
            entity = 'Evento'
        else:
            entity = 'Esporte'

        stats_columns = [
            {"name": entity, "id": "event_sport"},
            {"name": "Kurtosis", "id": "kurtosis"},
            {"name": "Entropia", "id": "entropy"}
        ]

        # Se múltiplos eventos/esportes são selecionados
        if len(selected_values) > 1:
            for value in selected_values:
                # Filtrar dados com base no tipo de filtro
                if filter_type == 'Event':
                    df_filtered = adjusted_df[adjusted_df['Event'] == value][selected_features]
                else:
                    df_filtered = adjusted_df[adjusted_df['Sport'] == value][selected_features]

                if df_filtered.empty:
                    continue

                # Aplicar PCA para redução de dimensionalidade
                pca = PCA(n_components=1)
                transformed = pca.fit_transform(df_filtered)

                # Calcular kurtosis e entropia
                kurt = kurtosis(transformed.squeeze())
                ent = entropy(np.histogram(transformed.squeeze(), bins=10)[0])

                # Adicionar dados à tabela
                stats_data.append({
                    "event_sport": value,
                    "kurtosis": f"{kurt:.2f}",
                    "entropy": f"{ent:.2f}"
                })

                # Dados para o gráfico KDE
                kde_data.append(transformed.squeeze())
                kde_labels.append(f'{value} (PCA)')

            # Criar gráfico KDE combinado
            if kde_data:
                kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)
            else:
                kde_fig = {}

        else:
            # Se apenas um evento/esporte é selecionado
            value = selected_values[0]

            if filter_type == 'Event':
                df_filtered = adjusted_df[adjusted_df['Event'] == value]
            else:
                df_filtered = adjusted_df[adjusted_df['Sport'] == value]

            if df_filtered.empty:
                return [], {}, [], [], [], ''

            # Calcular kurtosis e entropia para cada atributo
            for feature in selected_features:
                feature_data = df_filtered[feature]
                kurt = kurtosis(feature_data)
                ent = entropy(np.histogram(feature_data, bins=10)[0])

                stats_data.append({
                    "event_sport": f'{value} - {feature}',
                    "kurtosis": f"{kurt:.2f}",
                    "entropy": f"{ent:.2f}"
                })

                kde_data.append(feature_data)
                kde_labels.append(feature)

            # Criar gráfico KDE para cada atributo
            if kde_data:
                kde_fig = ff.create_distplot(kde_data, kde_labels, show_hist=False)
            else:
                kde_fig = {}

            # Calcular distâncias para eventos/esportes próximos
            selected_mean = df_filtered[selected_features].mean().values.reshape(1, -1)

            if filter_type == 'Event':
                other_values = df_gender['Event'].unique()
                group_df = df_gender.groupby('Event')
            else:
                other_values = df_gender['Sport'].unique()
                group_df = df_gender.groupby('Sport')


        return stats_data, kde_fig, stats_columns

#if __name__ == '__main__':
    #app.run_server(debug=True)
