import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

RESULTS = BASE / "data" / "results"

# --------------------------------------------------
# Load previously calculated criterion results
# --------------------------------------------------

highway = pd.read_csv(
    RESULTS / "highway_criterion_summary.csv"
)

waterbody = pd.read_csv(
    RESULTS / "waterbody_criterion_summary.csv"
)

wetland = pd.read_csv(
    RESULTS / "wetland_impact_summary.csv"
)

esz = pd.read_csv(
    RESULTS / "esz_impact_summary.csv"
)

# --------------------------------------------------
# Select the variables for the master dataset
# --------------------------------------------------

highway_selected = highway[
    [
        "route",
        "total_interaction_length_km"
    ]
].rename(
    columns={
        "total_interaction_length_km":
        "highway_interaction_km"
    }
)

waterbody_selected = waterbody[
    [
        "route",
        "nearest_waterbody_distance_m",
        "waterbodies_within_100m",
        "waterbodies_within_500m"
    ]
]

wetland_selected = wetland[
    [
        "route",
        "wetland_count",
        "wetland_area_ha"
    ]
]

esz_selected = esz[
    [
        "route",
        "intersecting_esz_count",
        "nearest_esz_distance_m"
    ]
]

# --------------------------------------------------
# Merge all criteria
# --------------------------------------------------

master = highway_selected.merge(
    waterbody_selected,
    on="route",
    how="outer"
)

master = master.merge(
    wetland_selected,
    on="route",
    how="outer"
)

master = master.merge(
    esz_selected,
    on="route",
    how="outer"
)

# --------------------------------------------------
# Sort routes
# --------------------------------------------------

route_order = {
    "Route 1": 1,
    "Route 2": 2,
    "Route 3": 3
}

master["route_order"] = master["route"].map(route_order)

master = (
    master
    .sort_values("route_order")
    .drop(columns=["route_order"])
    .reset_index(drop=True)
)

# --------------------------------------------------
# Display master dataset
# --------------------------------------------------

print()
print("=" * 100)
print("MASTER ROUTE CRITERIA DATASET")
print("=" * 100)

print(
    master.to_string(index=False)
)

# --------------------------------------------------
# Check missing values
# --------------------------------------------------

print()
print("=" * 100)
print("MISSING VALUE CHECK")
print("=" * 100)

print(
    master.isna().sum()
)

# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT = RESULTS / "master_route_criteria.csv"

master.to_csv(
    OUTPUT,
    index=False
)

print()
print("Master dataset saved to:")
print(OUTPUT)