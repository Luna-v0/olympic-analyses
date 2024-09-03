import pandas as pd

df = pd.read_csv("data/athlete_events.csv")

columns_to_drop = ['ID', 'Name', 'Sex', 'Age', 'Height', 'Weight', 'Team', 'NOC', 'Games',
       'Year', 'Season', 'City', 'Sport', 'Event']
df.dropna(subset=columns_to_drop, inplace=True)

df.fillna("No Medal", inplace=True)
df = df[df.Season == "Summer"]

sports_few_data_points = ["Motorboating", "Figure Skating", "Lacrosse"]
df = df[~df.Sport.isin(sports_few_data_points)]
df = df.drop(columns=["ID", "Name", "Team", "Games", "City", "Season"])

df.to_csv("data/polished.csv")