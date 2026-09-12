import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
# Load artisan pricing dataset
df = pd.read_csv("artisan_pricing_sample_8000.csv")
print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)
# Display basic information
print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])
# Check and handle missing values
print("\nMissing values:")
missing_count = df.isnull().sum().sum()
print("Total missing values:", missing_count)
if missing_count > 0:
    df = df.dropna()
    print("Rows containing missing values were removed.")
else:
    print("No missing values found.")
# Check and remove duplicate rows
print("\nDuplicate rows:")
duplicate_count = df.duplicated().sum()
print("Duplicate rows:", duplicate_count)
if duplicate_count > 0:
    df = df.drop_duplicates()
    print("Duplicate rows were removed.")
else:
    print("No duplicate rows found.")
# Check and remove invalid numerical values
print("\nValue validation:")
invalid_mask = (
    (df["material_cost"] < 0) |
    (df["production_time_days"] <= 0) |
    (df["demand_index"] < 0) |
    (df["demand_index"] > 1) |
    (df["actual_selling_price"] <= 0)
)
invalid_count = invalid_mask.sum()
print("Invalid numerical rows:", invalid_count)
if invalid_count > 0:
    df = df[~invalid_mask]
    print("Invalid numerical rows were removed.")
else:
    print("No invalid numerical values found.")
# Standardize text values
categorical_columns = [
    "product_category",
    "product_type",
    "material_type",
    "region",
    "origin_state",
    "season"
]
for column in categorical_columns:
    df[column] = df[column].str.strip()
print("\nText values standardized successfully.")
# Check and remove empty text values
print("\nEmpty text values:")
empty_mask = df[categorical_columns].eq("").any(axis=1)
empty_count = empty_mask.sum()
print("Rows with empty text values:", empty_count)
if empty_count > 0:
    df = df[~empty_mask]
    print("Rows with empty text values were removed.")
else:
    print("No empty text values found.")
# Display final dataset information
print("\nFinal dataset information:")
print("Final number of rows:", df.shape[0])
print("Final number of columns:", df.shape[1])
print("\nData types:")
print(df.dtypes)
# Display numerical validation
print("\nNumerical validation:")
print("Minimum material cost:", df["material_cost"].min())
print("Minimum production time:", df["production_time_days"].min())
print("Minimum demand index:", df["demand_index"].min())
print("Maximum demand index:", df["demand_index"].max())
print("Minimum market trend:", df["market_trend"].min())
print("Maximum market trend:", df["market_trend"].max())
print("Minimum selling price:", df["actual_selling_price"].min())
# Display numerical summary
print("\nNumerical summary:")
print(df[
    [
        "material_cost",
        "production_time_days",
        "demand_index",
        "market_trend",
        "actual_selling_price"
    ]
].describe())
# Final cleaning check
print("\nFinal cleaning check:")

print("Missing values:", df.isnull().sum().sum())
print("Duplicate rows:", df.duplicated().sum())

final_empty_count = df[categorical_columns].eq("").sum().sum()
print("Empty text values:", final_empty_count)
print("\nData cleaning and validation completed successfully.")
# Prepare features and target
feature_columns = [
    "product_category",
    "product_type",
    "material_cost",
    "production_time_days",
    "region",
    "origin_state",
    "demand_index",
    "market_trend",
    "material_type"
]
X = df[feature_columns]
y = df["actual_selling_price"]
print("\nFeatures and target prepared successfully.")
print("Feature columns:", X.columns.tolist())
print("Number of features:", X.shape[1])
print("Target column:", y.name)
# Separate numerical and categorical features
numerical_features = [
    "material_cost",
    "production_time_days",
    "demand_index",
    "market_trend"
]
categorical_features = [
    "product_category",
    "product_type",
    "region",
    "origin_state",
    "material_type"
]
print("\nNumerical features:", numerical_features)
print("Number of numerical features:", len(numerical_features))
print("\nCategorical features:", categorical_features)
print("Number of categorical features:", len(categorical_features))
# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    shuffle=True,
    random_state=42
)
print("\nTraining and testing data prepared successfully.")
print("Training features:", X_train.shape)
print("Testing features:", X_test.shape)
print("Training target:", y_train.shape)
print("Testing target:", y_test.shape)
# Encode categorical features and prepare numerical features
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"
)
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)
print("\nFeature encoding completed successfully.")
print("Processed training features:", X_train_processed.shape)
print("Processed testing features:", X_test_processed.shape)
# Train Random Forest model
random_forest_model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)
random_forest_model.fit(X_train_processed, y_train)
print("\nRandom Forest model trained successfully.")
# Evaluate Random Forest model
rf_predictions = random_forest_model.predict(X_test_processed)
rf_mae = mean_absolute_error(y_test, rf_predictions)
rf_rmse = mean_squared_error(y_test, rf_predictions) ** 0.5
rf_r2 = r2_score(y_test, rf_predictions)
print("\nRandom Forest evaluation:")
print("MAE:", rf_mae)
print("RMSE:", rf_rmse)
print("R2 Score:", rf_r2)
# Calculate prediction accuracy within price-error limits

rf_percentage_error = (
    abs(y_test - rf_predictions) / y_test
) * 100

rf_accuracy_10 = (rf_percentage_error <= 10).mean() * 100
rf_accuracy_15 = (rf_percentage_error <= 15).mean() * 100
rf_accuracy_20 = (rf_percentage_error <= 20).mean() * 100

print("\nRandom Forest prediction accuracy:")
print("Within ±10%:", rf_accuracy_10, "%")
print("Within ±15%:", rf_accuracy_15, "%")
print("Within ±20%:", rf_accuracy_20, "%")
# Calculate MAPE and overall prediction accuracy

rf_mape = (abs(y_test - rf_predictions) / y_test).mean() * 100
rf_accuracy = 100 - rf_mape

print("\nRandom Forest MAPE:", rf_mape, "%")
print("Random Forest overall prediction accuracy:", rf_accuracy, "%")
# Train XGBoost model
xgboost_model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    random_state=42,
    n_jobs=-1
)
xgboost_model.fit(X_train_processed, y_train)
print("\nXGBoost model trained successfully.")
# Evaluate XGBoost model
xgb_predictions = xgboost_model.predict(X_test_processed)
xgb_mae = mean_absolute_error(y_test, xgb_predictions)
xgb_rmse = mean_squared_error(y_test, xgb_predictions) ** 0.5
xgb_r2 = r2_score(y_test, xgb_predictions)
print("\nXGBoost evaluation:")
print("MAE:", xgb_mae)
print("RMSE:", xgb_rmse)
print("R2 Score:", xgb_r2)
# Calculate XGBoost prediction accuracy within price-error limits

xgb_percentage_error = (
    abs(y_test - xgb_predictions) / y_test
) * 100

xgb_accuracy_10 = (xgb_percentage_error <= 10).mean() * 100
xgb_accuracy_15 = (xgb_percentage_error <= 15).mean() * 100
xgb_accuracy_20 = (xgb_percentage_error <= 20).mean() * 100

print("\nXGBoost prediction accuracy:")
print("Within ±10%:", xgb_accuracy_10, "%")
print("Within ±15%:", xgb_accuracy_15, "%")
print("Within ±20%:", xgb_accuracy_20, "%")
# Calculate XGBoost MAPE and overall prediction accuracy

xgb_mape = (abs(y_test - xgb_predictions) / y_test).mean() * 100
xgb_accuracy = 100 - xgb_mape

print("\nXGBoost MAPE:", xgb_mape, "%")
print("XGBoost overall prediction accuracy:", xgb_accuracy, "%")
# Prepare data for CatBoost
catboost_categorical_features = [
    "product_category",
    "product_type",
    "region",
    "origin_state",
    "material_type"
]
catboost_category_indices = [
    X_train.columns.get_loc(column)
    for column in catboost_categorical_features
]
print("\nCatBoost data prepared successfully.")
print("Categorical feature indices:", catboost_category_indices)
# Train CatBoost model
catboost_model = CatBoostRegressor(
    iterations=300,
    learning_rate=0.05,
    depth=6,
    random_seed=42,
    verbose=0
)
catboost_model.fit(
    X_train,
    y_train,
    cat_features=catboost_category_indices
)
print("\nCatBoost model trained successfully.")
# Evaluate CatBoost model
catboost_predictions = catboost_model.predict(X_test)
catboost_mae = mean_absolute_error(y_test, catboost_predictions)
catboost_rmse = mean_squared_error(y_test, catboost_predictions) ** 0.5
catboost_r2 = r2_score(y_test, catboost_predictions)
print("\nCatBoost evaluation:")
print("MAE:", catboost_mae)
print("RMSE:", catboost_rmse)
print("R2 Score:", catboost_r2)
# Calculate CatBoost prediction accuracy within price-error limits
catboost_percentage_error = (
    abs(y_test - catboost_predictions) / y_test
) * 100
catboost_accuracy_10 = (catboost_percentage_error <= 10).mean() * 100
catboost_accuracy_15 = (catboost_percentage_error <= 15).mean() * 100
catboost_accuracy_20 = (catboost_percentage_error <= 20).mean() * 100
print("\nCatBoost prediction accuracy:")
print("Within ±10%:", catboost_accuracy_10, "%")
print("Within ±15%:", catboost_accuracy_15, "%")
print("Within ±20%:", catboost_accuracy_20, "%")
# Calculate CatBoost MAPE and overall prediction accuracy

catboost_mape = (
    abs(y_test - catboost_predictions) / y_test
).mean() * 100

catboost_accuracy = 100 - catboost_mape

print("\nCatBoost MAPE:", catboost_mape, "%")
print("CatBoost overall prediction accuracy:", catboost_accuracy, "%")