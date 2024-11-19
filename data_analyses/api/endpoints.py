import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json

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

    return df[index_column].tolist()

@app.get("/api/fairestSports")
def get_fairest(
        agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
        gender: str = Query(..., description="Gender")
) -> List[dict]:
    # Posso migrar o que já temos, mas acho que é retrabalho
    pass


@app.get("/api/getSportsForUser")
def get_sports_for_user(
        _user_data: str = Query(..., description="User data for retrieving sports."),
        agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
) -> List[dict]:
    try: # Eu acabei de descobrir q o fastapi tem um problema com INPUTS de dict pela forma de que ele encoda os dados na url
        # Então, eu tive que fazer esse workaround para que o fastapi aceite um dict como input
        user_data = json.loads(_user_data)
    except json.JSONDecodeError as e:
        return [{"error": "Invalid JSON data."}]
    
    # Features to use for the analysis
    used_columns = ['Height', 'BMI', 'Age', 'GDP']

    df, index_column = get_ic_and_df(agg_level)

    user_gender = user_data.get("Sex")
    df = df[df['Sex'] == user_gender]

    feature_means = df[used_columns].mean()
    feature_stds = df[used_columns].std()

    user_row = {
        'Height': user_data['Height'],
        'BMI': user_data['BMI'],
        'Age': user_data['Age'],
        'GDP': user_data['GDP'],
        index_column: "User"  # To identify the user row
    }
    df = pd.concat([df, pd.DataFrame([user_row])], ignore_index=True)

    df[used_columns] = (df[used_columns] - feature_means) / feature_stds

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
        features: List[str] = Query(..., description="List of features to calculate distances.")
) -> List[dict]:
    pass


@app.get("/api/timeTendencies")
def time_tendencies(
        data: List[str] = Query([], description="List of tendencies to analyze over time.")
) -> List[dict]:
    print(data)

    response = [
        {"date": "2026", "lines": {"soccer": 25, "shootiing": 17}},
        {"date": "2025", "lines": {"tennis": 20, "soccer": 10, "shootiing": 17}},
        {"date": "2024", "lines": {"tennis": 25, "soccer": 30, "shootiing": 17}},
        {"date": "2021", "lines": {"tennis": 10, "soccer": 20}},
    ]

    return response