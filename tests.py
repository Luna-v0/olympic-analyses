import pandas as pd

df = pd.read_csv("D:\olympic-analyses\data\polished3_with_gdp.csv")
print(df['Event'].unique())
