# utils.py
import pandas as pd

def adjust_medals(dataframe, medal_multiplier=2):
    copies = dataframe[dataframe['Won Medal'] == True].copy()

    # Use pd.concat to create n copies
    for _ in range(medal_multiplier - 2):  # we already have 1 copy
        copies = pd.concat([copies, dataframe[dataframe['Won Medal'] == True]])

    # Concatenate original DataFrame with the new copies
    df_with_copies = pd.concat([dataframe, copies], ignore_index=True)
    return df_with_copies
