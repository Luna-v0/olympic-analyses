import pandas as pd

columns = ['Sex', 'Age', 'Height', 'BMI', 'GDP', 'Sport', 'Event']
df = pd.read_csv("../data/polished3_with_moy_gdp.csv")
df = df[columns]

df.to_csv("../data/features.csv", index=False)