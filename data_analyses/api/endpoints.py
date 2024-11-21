import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
from sklearn.preprocessing import StandardScaler

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
def get_features(
        agg_level: str = Query(..., description="Aggregation level for the features. (Sport or event)"),
        names: List[str] = Query(..., description="List of sports/event names.")
) -> List[dict]:
    if agg_level == "Sport":
        index_column = "Sport"
    elif agg_level == "Event":
        index_column = "Event"
    else:
        return [{"error": "Invalid agg_level. Must be 'Sport' or 'Event'."}]

    df = pd.read_csv("../data/features.csv")
    filtered_df = df[df[index_column].isin(names)]
    response = filtered_df.to_dict(orient="records")

    return response

@app.get("/api/getNames")
def get_names(
    agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
) -> List[str]:
    df, index_column = get_ic_and_df(agg_level)
    if index_column is None: return []
    return df[index_column].tolist()

@app.get("/api/fairestSports")
def get_fairest(
        agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
        gender: str = Query(..., description="Gender")
) -> List[dict]:
    pass


@app.get("/api/getSportsForUser")
def get_sports_for_user(
    _user_data: str = Query(..., description="User data for retrieving sports."),
    agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
) -> List[dict]:
    try:
        user_data = json.loads(_user_data)
    except json.JSONDecodeError:
        return [{"error": "Invalid JSON data."}]

    # Features to use for the analysis
    used_columns = ['Height', 'BMI', 'Age', 'GDP']

    df, index_column = get_ic_and_df(agg_level)

    user_gender = user_data.get("Sex")
    df = df[df['Sex'] == user_gender]

    gdp_df = pd.read_csv('noc_gdp.csv')
    df = df.merge(gdp_df, on='NOC', how='left')

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

    user_row = {
        'Height': (user_data['Height'] - feature_means['Height']) / feature_stds['Height'],
        'BMI': (user_data['BMI'] - feature_means['BMI']) / feature_stds['BMI'],
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
    return result



@app.get("/api/getSportsDistance")
def get_sports_distance(
        agg_level: str = Query(..., description="Aggregation level for sports distances."),
        sex: str = Query(ANY, description="Gender"),
        features: List[str] = Query(..., description="List of features to calculate distances.")
) -> List[dict]:
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
        isSportsOrEvents: str = Query(..., description="String with either 'sports' or 'events'"),
        feature: str = Query(..., description="Feature to analyze over time."),
        sportsOrEvents: List[str] = Query([], description="List of Sports or Events to analyze."),
) -> List[dict]:
    import pandas as pd

    if isSportsOrEvents.lower() not in ['sports', 'events']:
        return [{"error": "isSportsOrEvents must be 'sports' or 'events'"}]

    try:
        df = pd.read_csv("../data/athlete_events.csv")
    except FileNotFoundError:
        return [{"error": "Data file not found."}]

    if feature not in df.columns:
        return [{"error": f"Feature '{feature}' not found in data"}]

    if not sportsOrEvents:
        if isSportsOrEvents.lower() == 'sports':
            sportsOrEvents = df['Sport'].dropna().unique().tolist()
        else:
            sportsOrEvents = df['Event'].dropna().unique().tolist()

    if isSportsOrEvents.lower() == 'sports':
        df_filtered = df[df['Sport'].isin(sportsOrEvents)].copy()
        group_column = 'Sport'
    else:
        df_filtered = df[df['Event'].isin(sportsOrEvents)].copy()
        group_column = 'Event'

    df_filtered = df_filtered.dropna(subset=['Year', feature])

    if df_filtered.empty:
        return []

    df_filtered['Year'] = df_filtered['Year'].astype(int).astype(str)

    if pd.api.types.is_numeric_dtype(df_filtered[feature]):
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].mean().reset_index()
    else:
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].agg(lambda x: x.mode().iloc[0]).reset_index()

    if df_grouped.empty:
        return []

    df_pivot = df_grouped.pivot(index='Year', columns=group_column, values=feature)

    if df_pivot.empty:
        return []

    df_pivot.reset_index(inplace=True)

    response = []
    for idx, row in df_pivot.iterrows():
        date = row['Year']
        lines = {}
        for sport_or_event in sportsOrEvents:
            if sport_or_event in df_pivot.columns:
                value = row[sport_or_event]
                if pd.notnull(value):
                    lines[sport_or_event] = value
        if lines:
            response.append({"date": date, "lines": lines})

    return response

