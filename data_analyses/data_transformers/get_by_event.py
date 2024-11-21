import pandas as pd

columns = ['Age', 'Height', 'BMI', 'GDP', 'Event', 'Sex']
df = pd.read_csv("../data/features.csv")
df = df[columns]
aggregated_df = df.groupby(['Event', 'Sex'], as_index=False).mean()
aggregated_df.to_csv("../data/by_event.csv", index=False)
