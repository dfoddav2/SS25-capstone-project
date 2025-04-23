import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn import tree
from sklearn.metrics import r2_score, mean_squared_error
import xgboost as xgb

# Load the data
df = pd.read_parquet("../all_car_details.parquet")
print("Data loaded successfully.")
print(f"Data shape: {df.shape}")

# Data cleaning and preprocessing (same as in notebook)
df.drop(columns=["url", "electric_range", "model_code",
                 "manufacturer_colour", "country_version", "general_inspection"], inplace=True)
df = df[df['price'].notnull()]
upper_price_threshold = df['price'].quantile(0.99)
lower_price_threshold = df['price'].quantile(0.01)
df_cleaned = df[(df['price'] < upper_price_threshold) & (
    df['price'] > lower_price_threshold)].copy()
df_cleaned['first_registration'] = pd.to_datetime(
    df_cleaned['first_registration'], format='%Y-%m', errors='coerce')
current_date = pd.to_datetime('now')
df_cleaned['age_months'] = (current_date.year - df_cleaned['first_registration'].dt.year) * \
    12 + (current_date.month - df_cleaned['first_registration'].dt.month)
df_cleaned.drop(columns=['first_registration'], inplace=True, axis=1)
df_cleaned = df_cleaned[df_cleaned['age_months'] >= 0]
print(f"Data shape after cleaning: {df_cleaned.shape}")


def convert_fuel_consumption(val):
    if pd.isna(val):
        return np.nan
    match = re.search(r"[\d\.]+", val)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return np.nan
    return np.nan


if df_cleaned['fuel_consumption'].dtype != 'float64':
    df_cleaned['fuel_consumption'] = df_cleaned['fuel_consumption'].apply(
        convert_fuel_consumption)
numeric_cols = ['seats', 'doors', 'gears', 'cylinders']
for col in numeric_cols:
    df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

print("Converted fuel consumption and numeric columns to float.")
df_cleaned_split = df_cleaned.copy()


def process_semicolon_column(df, colname, delimiter=';'):
    new_colname = f"{colname}_list"

    def split_values(val):
        if pd.isna(val):
            return None
        return [item.strip() for item in val.split(delimiter) if item.strip()]

    df[new_colname] = df[colname].apply(split_values)
    not_missing = df[new_colname].notna()
    if not not_missing.any():
        print(f"No non-missing values found in {colname}")
        return df
    mlb = MultiLabelBinarizer()
    encoded = pd.DataFrame(mlb.fit_transform(df.loc[not_missing, new_colname]),
                           columns=mlb.classes_,
                           index=df.loc[not_missing].index)
    df = pd.concat([df, encoded], axis=1)
    return df


columns_to_process = ['comfort_and_convenience',
                      'entertainment_and_media', 'safety_and_security', 'extras']
for col in columns_to_process:
    df_cleaned_split = process_semicolon_column(df_cleaned_split, col)
    df_cleaned_split.drop(columns=[col, f"{col}_list"], inplace=True)

df_cleaned_split['location'] = df_cleaned_split['location'].apply(
    lambda loc: loc.split(', ')[-1].strip() if pd.notna(loc) else None)
df_cleaned_split['location'] = df_cleaned_split['location'].str.extract(
    r'([A-Za-z]{2})')
print("Processed semicolon-separated columns and location.")


# Prepare data for XGBoost
X = df_cleaned_split.drop(columns=['price', 'car_title'])
X = pd.get_dummies(X, drop_first=True)
y = df_cleaned_split['price']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print("Training model...")
# Train XGBoost model
xgb_model = xgb.XGBRegressor(
    random_state=42,
    n_estimators=100,
    learning_rate=0.1,
    tree_method='hist'
)
xgb_model.fit(X_train, y_train)

# Evaluate
y_pred = xgb_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"XGBoost R²: {r2:.3f}")
print(f"XGBoost RMSE: {rmse:.2f}")
