import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the datasets
features_df = pd.read_csv("../data/features.csv")
global_dist_df = pd.read_csv("../data/global_distribution.csv")

# Filter for Male and Shooting
features_df = features_df[(features_df["Sex"] == "M") & (features_df["Sport"] == "Wrestling")]
global_dist_df = global_dist_df[global_dist_df["Sex"] == "M"]

# Features to compare
features = ["Age", "Height", "BMI"]

# Select only the relevant columns
global_dist_df = global_dist_df[features]
features_df = features_df[features]

# Plot distributions
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for i, feature in enumerate(features):
    # Calculate the combined min and max for consistent bins
    min_value = min(features_df[feature].min(), global_dist_df[feature].min())
    max_value = max(features_df[feature].max(), global_dist_df[feature].max())

    # Define bins
    bins = np.linspace(min_value, max_value, 25)

    # Plot histograms with density=True to normalize the areas
    axes[i].hist(global_dist_df[feature], bins=bins, alpha=0.5, label="Global Distribution", color='blue', density=True)
    axes[i].hist(features_df[feature], bins=bins, alpha=0.5, label="Shooting Athletes", color='orange', density=True)

    # Set titles and labels
    axes[i].set_title(f'Distribution of {feature}')
    axes[i].set_xlabel(feature)
    axes[i].set_ylabel('Density')
    axes[i].legend()

plt.tight_layout()
plt.show()
