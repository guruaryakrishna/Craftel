import pandas as pd
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