from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import json
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Union
import pandas as pd
from scipy.stats import ks_2samp
import numpy as np

# Agg levels
SPORT = "Sport"
EVENT = "Event"

# Gender
M = "M"
F = "F"
ANY = "ANY"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # HTTP methods: GET, POST, PUT, etc.
    allow_headers=["*"],  # Headers like Content-Type, Authorization, etc.
)

# List of features for POST endpoints
FEATURES = [
    "Name", "Age", "Height", "Weight", "Team", "NOC", "Games", "Year", 
    "City", "Sport", "Event", "Medal", "BMI"
]

# Helper function to load data
def load_data():
    try:
        return pd.read_csv("../data/athlete_events.csv")
    except FileNotFoundError:
        return pd.DataFrame()  # Return empty DataFrame if file is not found

# Helper function to save data
def save_data(df):
    df.to_csv("../data/athlete_events.csv", index=False)

@app.get("/api")
def read_root(data:str) -> dict:
    return {
        data: data,
    }

def get_ic_and_df(agg_level:str):
    df = None,
    index_column = None
    if agg_level == "Sport":
        df = pd.read_csv("../data/by_sport.csv")
        index_column = SPORT
    elif agg_level == "Event":
        df = pd.read_csv("../data/by_event.csv")
        index_column = EVENT

    return df, index_column

def filter_for_sex(df:pd.DataFrame, sex:str):
    if sex == ANY: return df
    return df[df["Sex"] == sex]

# Isso aqui é pra quando vocês precisarem de qq dado de um esporte ou evento
# agg_level = esporte ou evento
@app.get("/api/getFeatures")
def get_features_agg(
        agg_level: str = Query(..., description="Aggregation level for the features. (Sport or event)"),
        names: List[str] = Query(..., description="List of sports/event names."),
        gender: str = Query(ANY, description="Gender")
) -> List[dict]:
    df, index_column = get_ic_and_df(agg_level)
    if index_column is None: return []
    df = filter_for_sex(df, gender)
    filtered_df = df[df[index_column].isin(names)]
    response = filtered_df.to_dict(orient="records")

    return sorted(response)

@app.get("/api/getNames")
def get_names(
    agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
    gender: str = Query(ANY, description="Gender")

) -> List[str]:
    df, index_column = get_ic_and_df(agg_level)
    df = filter_for_sex(df, gender)
    if index_column is None: return []
    return sorted(df[index_column].tolist())


# Isso pode ser preprocessado bem facilmente, se performance for um problema
@app.get("/api/fairestSports")
def get_fairest(
        agg_level: str = Query("Sport", description="Aggregation (Sport or Event) level for fairest sports."),
        names: List[str] = Query([], description="List of sports to be returned"),
        gender: str = Query("M", description="Gender")
) -> List[dict]:
    df = pd.read_csv("../data/features.csv")
    global_dist = pd.read_csv("../data/global_distribution.csv")
    df = filter_for_sex(df, gender)

    features = ['Age', 'Height', 'BMI']

    grouped = df.groupby(agg_level)

    result = []

    global_data = {}
    for feature in features:
        global_data[feature] = global_dist[feature].dropna()

    # Distance collection for normalization
    all_feature_distances = {feature: [] for feature in features}

    for group_name, group_df in grouped:
        group_result = {"Name": group_name}
        for feature in features:
            group_feature_data = group_df[feature].dropna()

            ks_statistic, _ = ks_2samp(group_feature_data, global_data[feature])
            group_result[feature] = ks_statistic  # KS statistic as distance
            all_feature_distances[feature].append(ks_statistic)  # Collect for normalization
        result.append(group_result)

    # Normalize feature distances
    for feature in features:
        max_distance = max(all_feature_distances[feature])
        min_distance = min(all_feature_distances[feature])
        if max_distance > 0:  # Avoid division by zero
            for group in result:
                group[feature] = (group[feature] - min_distance) / (max_distance - min_distance)
                group[feature] = 1 - group[feature]

    for group in result:
        normalized_distances = [group[feature] for feature in features]
        group['total'] = round(np.sqrt(np.sum(np.square(normalized_distances))), 3)

    result = sorted(result, key=lambda x: x['total'])
    to_return = [x for x in result if x['Name'] in names]
    return to_return

@app.get("/api/getSportsToCompareWithUser")
def generateAverage(eventOrSport:str, gender:str):
    eventOrSport = eventOrSport.lower()
    #if starts with event
    if eventOrSport.startswith("event"):
        df = pd.read_csv("../data/yourEvents.csv")
    else:
        df = pd.read_csv("../data/yourSports.csv")
    
    df = df[df['Sex'] == gender]
    df = df.drop(columns=['Sex'])
    print(df.columns)
    return df.to_dict('records')

@app.get("/api/getSportsForUser")
def get_sports_for_user(
    _user_data: str = Query(..., description="User data for retrieving sports."),
    agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
) -> List:
    try:
        user_data = json.loads(_user_data)
    except json.JSONDecodeError:
        return [{"error": "Invalid JSON data."}]

    # Features to use for the analysis
    used_columns = ['Height', 'BMI', 'Age', 'GDP']

    df, index_column = get_ic_and_df(agg_level)

    user_gender = user_data.get("Sex")
    df = df[df['Sex'] == user_gender]

    gdp_df = pd.read_csv('../data/noc_gdp.csv')

    feature_means = df[used_columns].mean()
    feature_stds = df[used_columns].std()

    df[used_columns] = (df[used_columns] - feature_means) / feature_stds

    user_noc = user_data.get('NOC')
    if not user_noc:
        return [{"error": "User NOC is missing."}]

    user_gdp_row = gdp_df[gdp_df['NOC'] == user_noc]
    if user_gdp_row.empty:
        return [{"error": "User NOC not found in GDP data."}]

    user_gdp = user_gdp_row.iloc[0]['GDP']

    if 'Weight' not in user_data or 'Height' not in user_data:
        return [{"error": "User weight and height are required to calculate BMI."}]
    user_bmi = user_data['Weight'] / ((user_data['Height'] / 100) ** 2)

    user_row = {
        'Height': (user_data['Height'] - feature_means['Height']) / feature_stds['Height'],
        'BMI': (user_bmi - feature_means['BMI']) / feature_stds['BMI'],
        'Age': (user_data['Age'] - feature_means['Age']) / feature_stds['Age'],
        'GDP': (user_gdp - feature_means['GDP']) / feature_stds['GDP'],
        'Sex': user_data['Sex'],
        'NOC': user_noc,
        index_column: "User"  # To identify the user row
    }

    df = pd.concat([df, pd.DataFrame([user_row])], ignore_index=True)

    user_index = df[df[index_column] == "User"].index[0]
    user_features = df.loc[user_index, used_columns].values
    df['Distance'] = df[used_columns].apply(
        lambda row: np.linalg.norm(row - user_features), axis=1
    )

    df = df[df[index_column] != "User"]

    result = df[[index_column, 'Distance']].sort_values(by='Distance').to_dict(orient='records')
    return [result, user_gdp]



@app.get("/api/getSportsDistance")
def get_sports_distance(
        agg_level: str = Query('Sport' , description="Aggregation level for sports distances."),
        sex: str = Query(ANY, description="Gender"),
        features: List[str] = Query(['Height', 'Weight', 'Age', 'GDP'], description="List of features to calculate distances.")
) -> List[dict]:
    print(agg_level, sex, features)
    df, index_column = get_ic_and_df(agg_level)
    df = filter_for_sex(df, sex)
    scaler = StandardScaler()

    df[features] = scaler.fit_transform(df[features])

    distances = []
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i >= j:
                continue
            distance = np.linalg.norm(row1[features].values - row2[features].values)
            distances.append({
                f"{index_column}_1": row1[index_column],
                f"{index_column}_2": row2[index_column],
                "Distance": distance
            })

    sorted_distances = sorted(distances, key=lambda x: x["Distance"])
    return sorted_distances

@app.get("/api/timeTendencies")
def time_tendencies(
    isSportsOrEvents: str = Query("sports", description="String with either 'sports' or 'events'"),
    feature: str = Query("Height", description="Feature to analyze over time."),
    sportsOrEvents: List[str] = Query([], description="List of Sports or Events to analyze."),
) -> List[dict]:
    print(isSportsOrEvents, feature, sportsOrEvents)
    try:
        df = pd.read_csv("../data/athlete_events.csv")
    except FileNotFoundError:
        return [{"error": "Arquivo de dados não encontrado."}]
    except Exception as e:
        return [{"error": f"Erro inesperado ao carregar os dados: {str(e)}"}]

    # Normaliza o valor de isSportsOrEvents para minúsculas
    is_sports_or_events = isSportsOrEvents.lower()

    # Determina a coluna de agrupamento com base em isSportsOrEvents
    if is_sports_or_events.startswith('sport'):
        group_column = SPORT
    elif is_sports_or_events.startswith('event'):
        group_column = EVENT
    else:
        return [{"error": "isSportsOrEvents deve ser 'sports' ou 'events'."}]

    # Verifica se a feature existe no DataFrame
    if feature not in df.columns:
        return [{"error": f"Feature '{feature}' não encontrada nos dados."}]

    # Se a lista de sportsOrEvents estiver vazia, seleciona todos os disponíveis
    if not sportsOrEvents:
        sportsOrEvents = df[group_column].dropna().unique().tolist()

  # Filtra o DataFrame com base nos esportes/eventos selecionados e remove linhas com valores nulos em 'Year' ou na feature
    df_filtered = df[df[group_column].isin(sportsOrEvents)]
    df_filtered = df_filtered.dropna(subset=['Year', feature])

    if df_filtered.empty:
        return [{"error": "Nenhum dado disponível para os filtros fornecidos."}]

    # Converte a coluna 'Year' para string
    df_filtered['Year'] = df_filtered['Year'].astype(int).astype(str)

    # Agrupa os dados por 'Year' e pela coluna de agrupamento, calculando a média para features numéricas ou a moda para não numéricas
    if pd.api.types.is_numeric_dtype(df_filtered[feature]):
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].mean().reset_index()
    else:
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].agg(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        ).reset_index()

    if df_grouped.empty:
        return [{"error": "Nenhum dado após o agrupamento e análise."}]

    # Transforma os dados agrupados em um formato pivot para facilitar a criação de séries temporais
    df_pivot = df_grouped.pivot(index='Year', columns=group_column, values=feature)

    if df_pivot.empty:
        return [{"error": "Nenhum dado após a transformação pivot."}]

    df_pivot.reset_index(inplace=True)

    # Prepara a resposta no formato esperado pelo frontend
    response = []
    for _, row in df_pivot.iterrows():
        date = row['Year']
        lines = {}
        for sport_or_event in sportsOrEvents:
            if sport_or_event in df_pivot.columns:
                value = row.get(sport_or_event)
                if pd.notnull(value):
                    lines[sport_or_event] = value
        if lines:
            response.append({"date": date, "lines": lines})
    print(response)
    return response

