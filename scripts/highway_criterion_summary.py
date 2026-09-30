import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = (
    BASE
    / "data"
    / "results"
    / "highway_interaction_classified.csv"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "highway_criterion_summary.csv"
)

df = pd.read_csv(INPUT)

# --------------------------------------------------
# Route-level highway criterion metrics
# --------------------------------------------------

summary = (
    df.groupby("route")
    .agg(
        total_interactions=(
            "route",
            "size"
        ),

        total_interaction_length_km=(
            "intersection_length_km",
            "sum"
        ),

        short_crossing_count=(
            "interaction_type",
            lambda x: (
                x == "Short / Crossing-type"
            ).sum()
        ),

        extended_overlap_count=(
            "interaction_type",
            lambda x: (
                x == "Extended / Overlap-type"
            ).sum()
        ),

        short_crossing_length_km=(
            "intersection_length_km",
            lambda x: 0
        )
    )
    .reset_index()
)

# --------------------------------------------------
# Calculate lengths by interaction type
# --------------------------------------------------

short_length = (
    df[
        df["interaction_type"]
        == "Short / Crossing-type"
    ]
    .groupby("route")["intersection_length_km"]
    .sum()
)

extended_length = (
    df[
        df["interaction_type"]
        == "Extended / Overlap-type"
    ]
    .groupby("route")["intersection_length_km"]
    .sum()
)

summary["short_crossing_length_km"] = (
    summary["route"]
    .map(short_length)
    .fillna(0)
)

summary["extended_overlap_length_km"] = (
    summary["route"]
    .map(extended_length)
    .fillna(0)
)

# --------------------------------------------------
# Percentage of interaction that is extended
# --------------------------------------------------

summary["extended_length_percentage"] = (
    summary["extended_overlap_length_km"]
    / summary["total_interaction_length_km"]
    * 100
)

# --------------------------------------------------
# National Highway interaction
# --------------------------------------------------

nh_length = (
    df[
        df["road_class"]
        == "National Highway"
    ]
    .groupby("route")["intersection_length_km"]
    .sum()
)

summary["national_highway_length_km"] = (
    summary["route"]
    .map(nh_length)
    .fillna(0)
)

# --------------------------------------------------
# State Expressway interaction
# --------------------------------------------------

se_length = (
    df[
        df["road_class"]
        == "State Expressway"
    ]
    .groupby("route")["intersection_length_km"]
    .sum()
)

summary["state_expressway_length_km"] = (
    summary["route"]
    .map(se_length)
    .fillna(0)
)

# --------------------------------------------------
# Other major road interaction
# --------------------------------------------------

other_length = (
    df[
        df["road_class"]
        == "Other Major Road"
    ]
    .groupby("route")["intersection_length_km"]
    .sum()
)

summary["other_major_road_length_km"] = (
    summary["route"]
    .map(other_length)
    .fillna(0)
)

# --------------------------------------------------
# Round values
# --------------------------------------------------

numeric_columns = summary.select_dtypes(
    include="number"
).columns

summary[numeric_columns] = summary[
    numeric_columns
].round(4)

# --------------------------------------------------
# Display
# --------------------------------------------------

print()
print("=" * 80)
print("HIGHWAY CRITERION SUMMARY")
print("=" * 80)

print(
    summary.to_string(index=False)
)

# --------------------------------------------------
# Save
# --------------------------------------------------

summary.to_csv(
    OUTPUT,
    index=False
)

print()
print("Saved to:")
print(OUTPUT)