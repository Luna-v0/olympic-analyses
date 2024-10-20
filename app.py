import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from site2 import layout as pergunta1_layout, register_callbacks as register_callbacks_pergunta1
from nn import layout as pergunta3_layout, register_callbacks as register_callbacks_pergunta3

# Inicializar o aplicativo Dash com estilos Bootstrap
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# Layout com localização e conteúdo dinâmico
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Monitora a URL
    
     # Barra de navegação
    html.Div([
    html.Button("Pergunta 1", 
                id='btn-site1', 
                n_clicks=0, 
                style={
                    'marginRight': '10px', 
                    'padding': '5px 10px',  # Ajustando o padding para diminuir a altura
                    'borderRadius': '10px'   # Bordas arredondadas
                }
            ),
    html.Button("Pergunta 3", 
                id='btn-site2', 
                n_clicks=0, 
                style={
                    'padding': '5px 10px',  # Ajustando o padding para diminuir a altura
                    'borderRadius': '10px'   # Bordas arredondadas
                }
            ),

    ], style={#'textAlign': 'center', 'marginBottom': '5px', 'marginTop': '5px', 'position': 'fixed'}),
              'position': 'fixed',
        'top': '0',
        'left': '0',
        'right': '0',
        'backgroundColor': 'white',
        'padding': '10px',
        'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
        'zIndex': '1000',
        'display': 'flex',
        'justifyContent': 'center'
    }),

    
    html.Div(style={'marginTop': '70px', 'padding': '20px'},id='page-content'),  # Conteúdo da página
])

# Callback para trocar as páginas com base na URL
@app.callback(
    dash.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname in ['/', '/p1']:
        current_page = '/p1'
        page_content = pergunta1_layout
    elif pathname == '/p3':
        current_page = '/p3'
        page_content = pergunta3_layout
    else:
        return html.Div("Página não encontrada", style={'textAlign': 'center', 'marginTop': '50px'})
    
    # Desativa o botão da página atual
    disable_btn1 = current_page == 'site1'
    disable_btn2 = current_page == 'site2'
    
    return page_content, disable_btn1, disable_btn2

# Registra os callbacks das duas páginas
register_callbacks_pergunta1(app)
register_callbacks_pergunta3(app)

# Callback para atualizar a URL ao clicar nos botões
@app.callback(
    Output('url', 'pathname'),
    [Input('btn-site1', 'n_clicks'),
     Input('btn-site2', 'n_clicks')]
)
def navigate(btn1_clicks, btn2_clicks):
 # Determina qual botão foi clicado
    ctx = dash.callback_context
    if not ctx.triggered:  # Verifica se algum botão foi clicado
        return '/'  # Retorna a página inicial se nenhum botão foi clicado

    # Identifica qual botão foi acionado
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'btn-site1':
        return '/p1'
    elif button_id == 'btn-site2':
        return '/p3'

    return '/'  # Retorna a página inicial por padrão


# Executa o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
