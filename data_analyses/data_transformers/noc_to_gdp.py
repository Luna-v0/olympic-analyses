import pandas as pd

df = pd.read_csv("../data/polished3_with_gdp.csv")

columns = ['NOC', 'GDP']
df = df[columns]

df = df.dropna(subset=['NOC', 'GDP'])

noc_gdp_df = df.groupby('NOC', as_index=False).mean()

noc_gdp_df.to_csv("../data/noc_gdp.csv", index=False)

print(noc_gdp_df)
