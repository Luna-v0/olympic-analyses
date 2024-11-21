import numpy as np
import pandas as pd

# Define the age groups and their counts
age_groups = [
    {'age_group': '0-4', 'count_M': 331889289, 'count_F': 315450649, 'age_min': 0, 'age_max': 4},
    {'age_group': '5-9', 'count_M': 351991008, 'count_F': 332121131, 'age_min': 5, 'age_max': 9},
    {'age_group': '10-14', 'count_M': 353666705, 'count_F': 331681954, 'age_min': 10, 'age_max': 14},
    {'age_group': '15-19', 'count_M': 335882343, 'count_F': 315258559, 'age_min': 15, 'age_max': 19},
    {'age_group': '20-24', 'count_M': 318912554, 'count_F': 300510028, 'age_min': 20, 'age_max': 24},
    {'age_group': '25-29', 'count_M': 308889349, 'count_F': 291429439, 'age_min': 25, 'age_max': 29},
    {'age_group': '30-34', 'count_M': 310384416, 'count_F': 294303405, 'age_min': 30, 'age_max': 34},
    {'age_group': '35-39', 'count_M': 301744799, 'count_F': 289424003, 'age_min': 35, 'age_max': 39},
    {'age_group': '40-44', 'count_M': 270991534, 'count_F': 263180352, 'age_min': 40, 'age_max': 44},
    {'age_group': '45-49', 'count_M': 240153677, 'count_F': 236696232, 'age_min': 45, 'age_max': 49},
    {'age_group': '50-54', 'count_M': 231342779, 'count_F': 232097236, 'age_min': 50, 'age_max': 54},
    {'age_group': '55-59', 'count_M': 206686596, 'count_F': 212285997, 'age_min': 55, 'age_max': 59},
    {'age_group': '60-64', 'count_M': 170525048, 'count_F': 180992721, 'age_min': 60, 'age_max': 64},
    {'age_group': '65-69', 'count_M': 138182244, 'count_F': 154357035, 'age_min': 65, 'age_max': 69},
    {'age_group': '70-74', 'count_M': 103998992, 'count_F': 124048996, 'age_min': 70, 'age_max': 74},
    {'age_group': '75-79', 'count_M': 65570812, 'count_F': 83217973, 'age_min': 75, 'age_max': 79},
    {'age_group': '80-84', 'count_M': 37166893, 'count_F': 53013079, 'age_min': 80, 'age_max': 84},
    {'age_group': '85-89', 'count_M': 18342182, 'count_F': 31348041, 'age_min': 85, 'age_max': 89},
    {'age_group': '90-94', 'count_M': 6038458, 'count_F': 13078242, 'age_min': 90, 'age_max': 94},
    {'age_group': '95-99', 'count_M': 1141691, 'count_F': 3389124, 'age_min': 95, 'age_max': 99},
    {'age_group': '100+', 'count_M': 110838, 'count_F': 476160, 'age_min': 100, 'age_max': 105},
]

def generate_positive_normal(mean, std, size):
    """Generate positive values from a normal distribution."""
    vals = np.random.normal(loc=mean, scale=std, size=size)
    while np.any(vals <= 0):
        n_negative = np.sum(vals <= 0)
        vals[vals <= 0] = np.random.normal(loc=mean, scale=std, size=n_negative)
    return vals

def generate_data_for_gender(sex, n_samples):
    counts = []
    age_mins = []
    age_maxs = []
    for ag in age_groups:
        counts.append(ag['count_M'] if sex == 'M' else ag['count_F'])
        age_mins.append(ag['age_min'])
        age_maxs.append(ag['age_max'])
    total_count = sum(counts)
    proportions = [count / total_count for count in counts]
    # Sample age groups according to proportions
    chosen_age_groups = np.random.choice(len(age_groups), size=n_samples, p=proportions)
    ages = []
    for idx in chosen_age_groups:
        age_min = age_mins[idx]
        age_max = age_maxs[idx]
        # Generate an age uniformly within the age range
        age = np.random.randint(age_min, age_max + 1)
        ages.append(age)
    # Generate Height and BMI
    if sex == 'M':
        height_mean = 173
        height_std = 6.35
        bmi_mean = 24.2
        bmi_std = 4.5
    else:
        height_mean = 159
        height_std = 5.59
        bmi_mean = 24.4
        bmi_std = 5
    heights = generate_positive_normal(height_mean, height_std, n_samples)
    bmis = generate_positive_normal(bmi_mean, bmi_std, n_samples)
    data = pd.DataFrame({
        'Age': ages,
        'Height': heights,
        'BMI': bmis,
        'Sex': sex
    })
    return data

# Generate datasets for both genders
data_male = generate_data_for_gender('M', 1000)
data_female = generate_data_for_gender('F', 1000)

# Combine datasets
data = pd.concat([data_male, data_female], ignore_index=True)

# Display first few rows
print(data.head())

# Optionally, save the dataset to a CSV file
data.to_csv('../data/global_distribution.csv', index=False)
