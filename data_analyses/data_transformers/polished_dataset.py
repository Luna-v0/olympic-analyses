import pandas as pd

base_file_path = '../data/'

df = pd.read_csv(base_file_path+"athlete_events.csv")

columns_to_drop = ['ID', 'Name', 'Sex', 'Age', 'Height', 'Weight', 'Team', 'NOC', 'Games',
       'Year', 'Season', 'City', 'Sport', 'Event']
df.dropna(subset=columns_to_drop, inplace=True)

df.fillna("No Medal", inplace=True)
df = df[df.Season == "Summer"]

sports_few_data_points = ["Motorboating", "Figure Skating", "Lacrosse", "Ice Hockey", "Rugby", "Tug-Of-War",
                           "Art Competitions"]
df = df[~df.Sport.isin(sports_few_data_points)]

df["Won Medal"] = df.Medal != "No Medal"
df["BMI"] = df["Weight"] / (df["Height"] / 100) ** 2
print(df.head(), df.shape)
df.to_csv(base_file_path+"polished2.csv")