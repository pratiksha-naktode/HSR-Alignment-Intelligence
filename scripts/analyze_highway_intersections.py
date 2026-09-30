import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = BASE / "data" / "results" / "highway_intersection_cleaned.csv"

df = pd.read_csv(INPUT)

print("Total records:", len(df))

# --------------------------------------------------
# ROUTE-LEVEL ANALYSIS
# --------------------------------------------------

for route in ["Route 1", "Route 2", "Route 3"]:

    r = df[df["route"] == route].copy()

    print()
    print("=" * 60)
    print(route)
    print("=" * 60)

    print("Records:", len(r))

    print(
        "Total intersection length (m):",
        round(r["intersection_length_m"].sum(), 2)
    )

    print(
        "Total intersection length (km):",
        round(r["intersection_length_km"].sum(), 4)
    )

    print(
        "Average intersection length (m):",
        round(r["intersection_length_m"].mean(), 2)
    )

    print(
        "Maximum intersection length (m):",
        round(r["intersection_length_m"].max(), 2)
    )

    print()
    print("Road classes:")

    print(
        r["road_class"]
        .value_counts(dropna=False)
    )

    print()
    print("Lane distribution:")

    print(
        r["lane_status_clean"]
        .value_counts(dropna=False)
    )

    print()
    print("Existing / Proposed / Under Construction:")

    print(
        r["status"]
        .value_counts(dropna=False)
    )

    print()
    print("Longest 5 intersection records:")

    print(
        r[
            [
                "road_name",
                "road_class",
                "lane_status_clean",
                "status",
                "intersection_length_m"
            ]
        ]
        .sort_values(
            "intersection_length_m",
            ascending=False
        )
        .head(5)
        .to_string(index=False)
    )

# --------------------------------------------------
# COMPARISON TABLE
# --------------------------------------------------

summary = (
    df.groupby("route")
    .agg(
        highway_records=("route", "size"),
        total_intersection_km=(
            "intersection_length_km",
            "sum"
        ),
        average_intersection_m=(
            "intersection_length_m",
            "mean"
        ),
        max_intersection_m=(
            "intersection_length_m",
            "max"
        ),
        national_highways=(
            "road_class",
            lambda x: (x == "National Highway").sum()
        ),
        state_expressways=(
            "road_class",
            lambda x: (x == "State Expressway").sum()
        ),
        other_major_roads=(
            "road_class",
            lambda x: (x == "Other Major Road").sum()
        )
    )
    .reset_index()
)

print()
print("=" * 60)
print("ROUTE COMPARISON")
print("=" * 60)

print(summary.to_string(index=False))