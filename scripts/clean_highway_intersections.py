import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = BASE / "data" / "results" / "highway_intersection_details.csv"
OUTPUT = BASE / "data" / "results" / "highway_intersection_cleaned.csv"

# Load intersection data
df = pd.read_csv(INPUT)

print("Original records:", len(df))

# --------------------------------------------------
# 1. Clean text columns
# --------------------------------------------------

text_columns = [
    "road_name",
    "road_type",
    "lane_status",
    "category",
    "status"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

# --------------------------------------------------
# 2. Standardize missing values
# --------------------------------------------------

missing_values = ["", "nan", "NaN", "None", "NULL", "null"]

for col in text_columns:
    df[col] = df[col].replace(missing_values, pd.NA)

# --------------------------------------------------
# 3. Validate lane status
# --------------------------------------------------

valid_lane_values = ["2L", "4L", "6L", "8L"]

df["lane_status_valid"] = df["lane_status"].isin(valid_lane_values)

df["lane_status_clean"] = df["lane_status"]

df.loc[
    ~df["lane_status_valid"],
    "lane_status_clean"
] = pd.NA

# --------------------------------------------------
# 4. Flag missing / unknown data
# --------------------------------------------------

df["road_name_missing"] = df["road_name"].isna()

df["lane_status_missing_or_unknown"] = (
    df["lane_status_clean"].isna()
)

# --------------------------------------------------
# 5. Convert intersection length to km
# --------------------------------------------------

df["intersection_length_km"] = (
    df["intersection_length_m"] / 1000
)

# --------------------------------------------------
# 6. Create a simple highway classification
# --------------------------------------------------

def classify_road(row):

    road_type = row["road_type"]

    if road_type == "National Highway":
        return "National Highway"

    if road_type == "State Expressway":
        return "State Expressway"

    if road_type == "Other Major Road":
        return "Other Major Road"

    return "Unknown"


df["road_class"] = df.apply(classify_road, axis=1)

# --------------------------------------------------
# 7. Save cleaned dataset
# --------------------------------------------------

df.to_csv(OUTPUT, index=False)

print()
print("========== CLEANING SUMMARY ==========")

print("Original records:", len(df))

print(
    "Missing road names:",
    df["road_name_missing"].sum()
)

print(
    "Missing/unknown lane values:",
    df["lane_status_missing_or_unknown"].sum()
)

print()
print("Valid lane values:")
print(
    df["lane_status_clean"]
    .value_counts(dropna=False)
)

print()
print("Road classes:")
print(
    df["road_class"]
    .value_counts(dropna=False)
)

print()
print("Cleaned file:")
print(OUTPUT)