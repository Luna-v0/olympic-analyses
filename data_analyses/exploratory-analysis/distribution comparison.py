# Load the datasets
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

features_df = pd.read_csv("../data/features.csv")
global_dist_df = pd.read_csv("../data/global_distribution.csv")

# Filter for Male and Triathlon
features_df = features_df[features_df["Sex"] == "M"]
triathlon_df = features_df[(features_df["Sport"] == "Shooting") & (features_df["Sex"] == "M")]

# Features to compare
features = ["Age", "Height", "BMI"]

# Plot distributions
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i, feature in enumerate(features):
    # Extract global distribution parameters
    global_mean = \
    global_dist_df[(global_dist_df["Feature"] == feature) & (global_dist_df["Sex"] == "M")]["Mean"].values[0]
    global_std = \
    global_dist_df[(global_dist_df["Feature"] == feature) & (global_dist_df["Sex"] == "M")]["Std"].values[0]

    # Generate a global distribution for plotting
    global_data = np.random.normal(global_mean, global_std, triathlon_df.shape[0])

    # Plot histograms
    bin_width = global_std / 4  # Set desired bin width

    # Calculate number of bins for global data and triathlon data
    num_bins_global = int((global_data.max() - global_data.min()) / bin_width)
    num_bins_triathlon = int((triathlon_df[feature].max() - triathlon_df[feature].min()) / bin_width)

    axes[i].hist(global_data, bins=num_bins_global, alpha=0.5, label="Global Distribution", color='blue')
    axes[i].hist(triathlon_df[feature], bins=num_bins_triathlon, alpha=0.5, label="Triathlon", color='orange')

plt.tight_layout()
plt.show()
