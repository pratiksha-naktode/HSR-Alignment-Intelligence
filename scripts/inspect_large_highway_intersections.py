import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = BASE / "data" / "results" / "highway_intersection_cleaned.csv"

df = pd.read_csv(INPUT)

# --------------------------------------------------
# Inspect unusually large highway intersections
# --------------------------------------------------

threshold = 300  # metres

large = df[
    df["intersection_length_m"] >= threshold
].copy()

large = large.sort_values(
    ["route", "intersection_length_m"],
    ascending=[True, False]
)

print()
print("=" * 70)
print("LARGE HIGHWAY INTERSECTIONS")
print("=" * 70)

print(
    "Threshold:",
    threshold,
    "metres"
)

print(
    "Records above threshold:",
    len(large)
)

print()

print(
    large[
        [
            "route",
            "road_name",
            "road_class",
            "lane_status_clean",
            "status",
            "gis_length_km",
            "intersection_length_m",
            "intersection_length_km"
        ]
    ].to_string(index=False)
)

# --------------------------------------------------
# Route-wise count of large intersections
# --------------------------------------------------

print()
print("=" * 70)
print("ROUTE-WISE LARGE INTERSECTION COUNT")
print("=" * 70)

print(
    large["route"]
    .value_counts()
    .sort_index()
)

# --------------------------------------------------
# Route-wise total length of large intersections
# --------------------------------------------------

print()
print("=" * 70)
print("ROUTE-WISE LARGE INTERSECTION LENGTH")
print("=" * 70)

large_summary = (
    large.groupby("route")
    .agg(
        large_intersection_count=(
            "intersection_length_m",
            "size"
        ),
        large_intersection_length_km=(
            "intersection_length_km",
            "sum"
        )
    )
    .reset_index()
)

print(
    large_summary.to_string(index=False)
)