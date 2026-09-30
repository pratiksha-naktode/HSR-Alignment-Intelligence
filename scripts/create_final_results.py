import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

MASTER_FILE = RESULTS / "master_route_criteria.csv"
NORMALIZED_FILE = RESULTS / "normalized_route_criteria.csv"
WEIGHTS_FILE = RESULTS / "ahp_weights.csv"
FINAL_FILE = RESULTS / "final_route_scores.csv"

OUTPUT_FILE = RESULTS / "FINAL_HSR_ROUTE_RESULTS.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

master = pd.read_csv(MASTER_FILE)
normalized = pd.read_csv(NORMALIZED_FILE)
weights = pd.read_csv(WEIGHTS_FILE)
final_scores = pd.read_csv(FINAL_FILE)


# --------------------------------------------------
# SELECT RAW CRITERIA
# --------------------------------------------------

raw_columns = [
    "route",
    "highway_interaction_km",
    "nearest_waterbody_distance_m",
    "waterbodies_within_100m",
    "waterbodies_within_500m",
    "wetland_count",
    "wetland_area_ha",
    "intersecting_esz_count",
    "nearest_esz_distance_m"
]

raw = master[raw_columns].copy()


# --------------------------------------------------
# SELECT NORMALIZED SCORES
# --------------------------------------------------

normalized_columns = [
    "route",
    "C1_highway_score",
    "C2_waterbody_score",
    "C3_wetland_score",
    "C4_esz_score"
]

norm = normalized[normalized_columns].copy()


# --------------------------------------------------
# SELECT AHP WEIGHTS
# --------------------------------------------------

weight_map = dict(
    zip(
        weights["criterion"],
        weights["weight"]
    )
)

# Store weights as constant columns so that the final
# CSV clearly documents the AHP model used.

norm["Highway_AHP_Weight"] = weight_map["Highway Impact"]
norm["Waterbody_AHP_Weight"] = weight_map["Waterbody Impact"]
norm["Wetland_AHP_Weight"] = weight_map["Wetland Impact"]
norm["ESZ_AHP_Weight"] = weight_map["ESZ Impact"]


# --------------------------------------------------
# SELECT FINAL CONTRIBUTIONS
# --------------------------------------------------

contribution_columns = [
    "route",
    "Highway_Contribution",
    "Waterbody_Contribution",
    "Wetland_Contribution",
    "ESZ_Contribution",
    "Final_Score"
]

final = final_scores[contribution_columns].copy()


# --------------------------------------------------
# MERGE EVERYTHING
# --------------------------------------------------

result = raw.merge(
    norm,
    on="route",
    how="inner"
)

result = result.merge(
    final,
    on="route",
    how="inner"
)


# --------------------------------------------------
# CALCULATE RANK
# --------------------------------------------------

result["Rank"] = (
    result["Final_Score"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


# --------------------------------------------------
# ORDER COLUMNS
# --------------------------------------------------

column_order = [
    "route",

    # Raw GIS criteria
    "highway_interaction_km",
    "nearest_waterbody_distance_m",
    "waterbodies_within_100m",
    "waterbodies_within_500m",
    "wetland_count",
    "wetland_area_ha",
    "intersecting_esz_count",
    "nearest_esz_distance_m",

    # Normalized criteria
    "C1_highway_score",
    "C2_waterbody_score",
    "C3_wetland_score",
    "C4_esz_score",

    # AHP weights
    "Highway_AHP_Weight",
    "Waterbody_AHP_Weight",
    "Wetland_AHP_Weight",
    "ESZ_AHP_Weight",

    # Weighted contributions
    "Highway_Contribution",
    "Waterbody_Contribution",
    "Wetland_Contribution",
    "ESZ_Contribution",

    # Final result
    "Final_Score",
    "Rank"
]

result = result[column_order]


# --------------------------------------------------
# SORT BY RANK
# --------------------------------------------------

result = result.sort_values(
    by="Rank"
)


# --------------------------------------------------
# ROUND VALUES
# --------------------------------------------------

numeric_columns = result.select_dtypes(
    include="number"
).columns

result[numeric_columns] = result[numeric_columns].round(6)


# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

print("=" * 100)
print("FINAL HSR ROUTE RESULTS")
print("=" * 100)

print()

print(
    result[
        [
            "Rank",
            "route",
            "Final_Score",
            "Highway_Contribution",
            "Waterbody_Contribution",
            "Wetland_Contribution",
            "ESZ_Contribution"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 100)
print("FINAL CONSOLIDATED FILE CREATED")
print("=" * 100)

print(OUTPUT_FILE)
print()

print("Columns:", len(result.columns))
print("Routes:", len(result))


# --------------------------------------------------
# FINAL CHECK
# --------------------------------------------------

if len(result) == 3:
    print("PASS: All 3 routes included.")
else:
    print("WARNING: Expected 3 routes.")

if result["Final_Score"].notna().all():
    print("PASS: All final scores present.")
else:
    print("WARNING: Missing final score detected.")

if result["Rank"].tolist() == [1, 2, 3]:
    print("PASS: Route ranking generated correctly.")
else:
    print("WARNING: Check route ranking.")