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
        df = pd.read_csv("data/by_sport.csv")
        index_column = SPORT
    elif agg_level == "Event":
        df = pd.read_csv("data/by_event.csv")
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

    return response

@app.get("/api/getNames")
def get_names(
    agg_level: str = Query(..., description="Aggregation (Sport or event) level for fairest sports."),
    gender: str = Query(ANY, description="Gender")

) -> List[str]:
    df, index_column = get_ic_and_df(agg_level)
    df = filter_for_sex(df, gender)
    if index_column is None: return []
    return df[index_column].tolist()


# Isso pode ser preprocessado bem facilmente, se performance for um problema
@app.get("/api/fairestSports")
def get_fairest(
        agg_level: str = Query("Sport", description="Aggregation (Sport or Event) level for fairest sports."),
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
        group_result = {agg_level: group_name}
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

    for group in result:
        normalized_distances = [group[feature] for feature in features]
        group['total'] = np.sqrt(np.sum(np.square(normalized_distances)))

    result = sorted(result, key=lambda x: x['total'])
    print(result)
    return result


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
    try:
        df = pd.read_csv("../data/athlete_events.csv")
    except FileNotFoundError:
        return [{"error": "Data file not found."}]
    except Exception as e:
        return [{"error": f"Unexpected error while loading data: {str(e)}"}]

    if feature not in df.columns:
        return [{"error": f"Feature '{feature}' not found in data"}]

    if isSportsOrEvents.lower() not in ['sports', 'events']:
        return [{"error": "isSportsOrEvents must be either 'sports' or 'events'"}]

    group_column = 'Sport' if isSportsOrEvents.lower() == 'sports' else 'Event'

    if not sportsOrEvents:
        sportsOrEvents = df[group_column].dropna().unique().tolist()

    df_filtered = df[df[group_column].isin(sportsOrEvents)].copy()
    df_filtered = df_filtered.dropna(subset=['Year', feature])

    if df_filtered.empty:
        return [{"error": "No data available for the given filters."}]

    df_filtered['Year'] = df_filtered['Year'].astype(int).astype(str)

    if pd.api.types.is_numeric_dtype(df_filtered[feature]):
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].mean().reset_index()
    else:
        df_grouped = df_filtered.groupby(['Year', group_column])[feature].agg(lambda x: x.mode().iloc[0]).reset_index()

    if df_grouped.empty:
        return [{"error": "No data after grouping and analysis."}]

    df_pivot = df_grouped.pivot(index='Year', columns=group_column, values=feature)
    if df_pivot.empty:
        return [{"error": "No data after pivot transformation."}]

    df_pivot.reset_index(inplace=True)

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

    return response
