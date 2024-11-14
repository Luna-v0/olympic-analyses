import pandas as pd

base_file_path = '../data/'


df = pd.read_csv(base_file_path+"polished2.csv")

filtered_df = df.groupby("Event").filter(lambda x: len(x) >= 10)

filtered_df.to_csv(base_file_path+"polished3.csv", index=False)