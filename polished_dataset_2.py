import pandas as pd

df = pd.read_csv("data/polished2.csv")

filtered_df = df.groupby("Event").filter(lambda x: len(x) >= 10)

filtered_df.to_csv("data/polished3.csv", index=False)