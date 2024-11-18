import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

# Agg levels
SPORT = "sport"
EVENT = "event"

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


@app.get("/api/fairestSports")
def get_fairest(
        agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
        gender: str = Query(..., description="Gender")
) -> List[dict]:
    pass


@app.get("/api/getSportsForUser")
def get_sports_for_user(
        user_data: Dict = Query(..., description="User data for retrieving sports.")
) -> List[dict]:
    pass


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