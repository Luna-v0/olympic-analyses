import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import kurtosis, entropy

# Load the dataset
df = pd.read_csv('data/polished3_with_gdp.csv')

# Define features for normalization and kurtosis/entropy analysis
FEATURES = ["Height", "BMI", "Age", "GDP"]

# List of sports and events grouped by gender
genders = ['M', 'F']

def calculate_kurtosis_entropy(data, features):
    """Calculates kurtosis and entropy for the selected features in the data."""
    stats = {}
    for feature in features:
        feature_data = data[feature].dropna()  # Ensure no NaN values
        if len(feature_data) == 0:
            continue

        # Calculate kurtosis and entropy
        kurt = kurtosis(feature_data)
        ent = entropy(np.histogram(feature_data, bins=10)[0])

        stats[feature] = {
            'kurtosis': kurt,
            'entropy': ent
        }
    return stats

def analyze_by_category(df, group_col, features):
    """Analyzes kurtosis and entropy for a category (Event/Sport) grouped by gender."""
    results = {'high_kurtosis': {}, 'low_kurtosis': {}, 'high_entropy': {}, 'low_entropy': {}}

    for gender in genders:
        df_gender = df.loc[df['Sex'] == gender]  # Using .loc for filtering
        categories = df_gender[group_col].unique()

        kurtosis_results = []
        entropy_results = []

        for category in categories:
            # Filter data by category (Event/Sport)
            df_category = df_gender.loc[df_gender[group_col] == category]  # Using .loc for filtering
            if df_category.empty:
                continue

            # Normalize the features
            scaler = StandardScaler()
            df_category[features] = scaler.fit_transform(df_category[features])

            # Calculate kurtosis and entropy
            stats = calculate_kurtosis_entropy(df_category, features)

            # Compute mean kurtosis/entropy across features
            mean_kurt = np.mean([stat['kurtosis'] for stat in stats.values()])
            mean_ent = np.mean([stat['entropy'] for stat in stats.values()])

            kurtosis_results.append((category, mean_kurt))
            entropy_results.append((category, mean_ent))

        # Sort by kurtosis and entropy
        kurtosis_results.sort(key=lambda x: x[1], reverse=True)
        entropy_results.sort(key=lambda x: x[1], reverse=True)

        kurtosis_results = [res for res in kurtosis_results if not np.isnan(res[1])]
        entropy_results = [res for res in entropy_results if not np.isnan(res[1])]

        # Store highest and lowest kurtosis/entropy
        results['high_kurtosis'][gender] = kurtosis_results[0] if kurtosis_results else None
        results['low_kurtosis'][gender] = kurtosis_results[-1] if kurtosis_results else None
        results['high_entropy'][gender] = entropy_results[0] if entropy_results else None
        results['low_entropy'][gender] = entropy_results[-1] if entropy_results else None

    return results

# Analyze both events and sports
event_results = analyze_by_category(df, 'Event', FEATURES)
sport_results = analyze_by_category(df, 'Sport', FEATURES)

# Print results
print("Event Results:")
for gender in genders:
    print(f"\nGender: {gender}")
    print(f"Highest Kurtosis Event: {event_results['high_kurtosis'][gender]}")
    print(f"Lowest Kurtosis Event: {event_results['low_kurtosis'][gender]}")
    print(f"Highest Entropy Event: {event_results['high_entropy'][gender]}")
    print(f"Lowest Entropy Event: {event_results['low_entropy'][gender]}")

print("\nSport Results:")
for gender in genders:
    print(f"\nGender: {gender}")
    print(f"Highest Kurtosis Sport: {sport_results['high_kurtosis'][gender]}")
    print(f"Lowest Kurtosis Sport: {sport_results['low_kurtosis'][gender]}")
    print(f"Highest Entropy Sport: {sport_results['high_entropy'][gender]}")
    print(f"Lowest Entropy Sport: {sport_results['low_entropy'][gender]}")
