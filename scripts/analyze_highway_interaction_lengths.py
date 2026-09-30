import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = (
    BASE
    / "data"
    / "results"
    / "highway_intersection_cleaned.csv"
)

df = pd.read_csv(INPUT)

# --------------------------------------------------
# 1. Basic statistics
# --------------------------------------------------

length = df["intersection_length_m"]

print()
print("=" * 70)
print("HIGHWAY INTERACTION LENGTH ANALYSIS")
print("=" * 70)

print("Total records:", len(df))

print()
print("Minimum:", round(length.min(), 2), "m")
print("Maximum:", round(length.max(), 2), "m")
print("Mean:", round(length.mean(), 2), "m")
print("Median:", round(length.median(), 2), "m")

print()
print("Percentiles:")

for p in [25, 50, 75, 90, 95, 99]:
    print(
        f"{p}th percentile:",
        round(length.quantile(p / 100), 2),
        "m"
    )

# --------------------------------------------------
# 2. Interaction length ranges
# --------------------------------------------------

bins = [
    0,
    5,
    10,
    20,
    50,
    100,
    200,
    500,
    1000,
    float("inf")
]

labels = [
    "0-5 m",
    "5-10 m",
    "10-20 m",
    "20-50 m",
    "50-100 m",
    "100-200 m",
    "200-500 m",
    "500-1000 m",
    ">1000 m"
]

df["length_range"] = pd.cut(
    length,
    bins=bins,
    labels=labels,
    include_lowest=True
)

print()
print("=" * 70)
print("INTERACTION LENGTH DISTRIBUTION")
print("=" * 70)

print(
    df["length_range"]
    .value_counts()
    .reindex(labels, fill_value=0)
)

# --------------------------------------------------
# 3. Route-wise distribution
# --------------------------------------------------

print()
print("=" * 70)
print("ROUTE-WISE MEDIAN AND TOTAL")
print("=" * 70)

route_summary = (
    df.groupby("route")
    .agg(
        interaction_count=("route", "size"),
        total_length_m=(
            "intersection_length_m",
            "sum"
        ),
        mean_length_m=(
            "intersection_length_m",
            "mean"
        ),
        median_length_m=(
            "intersection_length_m",
            "median"
        ),
        max_length_m=(
            "intersection_length_m",
            "max"
        )
    )
    .reset_index()
)

print(
    route_summary.to_string(index=False)
)

# --------------------------------------------------
# 4. Show shortest and longest interactions
# --------------------------------------------------

columns = [
    "route",
    "road_name",
    "road_class",
    "lane_status_clean",
    "status",
    "intersection_length_m"
]

print()
print("=" * 70)
print("10 SHORTEST INTERACTIONS")
print("=" * 70)

print(
    df[columns]
    .sort_values("intersection_length_m")
    .head(10)
    .to_string(index=False)
)

print()
print("=" * 70)
print("20 LONGEST INTERACTIONS")
print("=" * 70)

print(
    df[columns]
    .sort_values(
        "intersection_length_m",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)