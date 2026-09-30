import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = (
    BASE
    / "data"
    / "results"
    / "highway_intersection_cleaned.csv"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "highway_interaction_classified.csv"
)

df = pd.read_csv(INPUT)

# --------------------------------------------------
# Classification threshold
# --------------------------------------------------

THRESHOLD = 20

df["interaction_type"] = df[
    "intersection_length_m"
].apply(
    lambda x:
        "Short / Crossing-type"
        if x <= THRESHOLD
        else "Extended / Overlap-type"
)

# --------------------------------------------------
# Overall classification
# --------------------------------------------------

print()
print("=" * 70)
print("HIGHWAY INTERACTION CLASSIFICATION")
print("=" * 70)

print("Threshold:", THRESHOLD, "m")

print()
print("Overall classification:")

print(
    df["interaction_type"]
    .value_counts()
)

# --------------------------------------------------
# Route-wise classification
# --------------------------------------------------

print()
print("=" * 70)
print("ROUTE-WISE CLASSIFICATION")
print("=" * 70)

route_classification = (
    pd.crosstab(
        df["route"],
        df["interaction_type"]
    )
)

print(
    route_classification.to_string()
)

# --------------------------------------------------
# Route-wise length
# --------------------------------------------------

print()
print("=" * 70)
print("ROUTE-WISE INTERACTION LENGTH")
print("=" * 70)

summary = (
    df.groupby(
        ["route", "interaction_type"]
    )
    .agg(
        count=(
            "intersection_length_m",
            "size"
        ),
        total_length_m=(
            "intersection_length_m",
            "sum"
        ),
        mean_length_m=(
            "intersection_length_m",
            "mean"
        )
    )
    .reset_index()
)

print(
    summary.to_string(index=False)
)

# --------------------------------------------------
# Extended overlap records
# --------------------------------------------------

print()
print("=" * 70)
print("EXTENDED / OVERLAP-TYPE INTERACTIONS")
print("=" * 70)

overlap = df[
    df["interaction_type"]
    == "Extended / Overlap-type"
].copy()

overlap = overlap.sort_values(
    "intersection_length_m",
    ascending=False
)

print(
    overlap[
        [
            "route",
            "road_name",
            "road_class",
            "lane_status_clean",
            "status",
            "intersection_length_m"
        ]
    ].to_string(index=False)
)

# --------------------------------------------------
# Save classified dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT,
    index=False
)

print()
print("Classified dataset saved to:")
print(OUTPUT)