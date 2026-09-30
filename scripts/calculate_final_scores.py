import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

NORMALIZED_FILE = RESULTS / "normalized_route_criteria.csv"
WEIGHTS_FILE = RESULTS / "ahp_weights.csv"
OUTPUT_FILE = RESULTS / "final_route_scores.csv"


# --------------------------------------------------
# LOAD FILES
# --------------------------------------------------

normalized = pd.read_csv(NORMALIZED_FILE)
weights_df = pd.read_csv(WEIGHTS_FILE)

print("=" * 80)
print("NORMALIZED CRITERIA")
print("=" * 80)

print(normalized)


print()
print("=" * 80)
print("AHP WEIGHTS")
print("=" * 80)

print(weights_df)


# --------------------------------------------------
# GET AHP WEIGHTS
# --------------------------------------------------

weights = dict(
    zip(
        weights_df["criterion"],
        weights_df["weight"]
    )
)

w_highway = weights["Highway Impact"]
w_waterbody = weights["Waterbody Impact"]
w_wetland = weights["Wetland Impact"]
w_esz = weights["ESZ Impact"]


# --------------------------------------------------
# CALCULATE WEIGHTED CONTRIBUTIONS
# --------------------------------------------------

normalized["Highway_Contribution"] = (
    normalized["C1_highway_score"] * w_highway
)

normalized["Waterbody_Contribution"] = (
    normalized["C2_waterbody_score"] * w_waterbody
)

normalized["Wetland_Contribution"] = (
    normalized["C3_wetland_score"] * w_wetland
)

normalized["ESZ_Contribution"] = (
    normalized["C4_esz_score"] * w_esz
)


# --------------------------------------------------
# FINAL SCORE
# --------------------------------------------------

normalized["Final_Score"] = (
    normalized["Highway_Contribution"]
    + normalized["Waterbody_Contribution"]
    + normalized["Wetland_Contribution"]
    + normalized["ESZ_Contribution"]
)


# --------------------------------------------------
# SELECT RESULTS
# --------------------------------------------------

result = normalized[
    [
        "route",
        "C1_highway_score",
        "C2_waterbody_score",
        "C3_wetland_score",
        "C4_esz_score",
        "Highway_Contribution",
        "Waterbody_Contribution",
        "Wetland_Contribution",
        "ESZ_Contribution",
        "Final_Score"
    ]
].copy()


# --------------------------------------------------
# SORT BY FINAL SCORE
# --------------------------------------------------

result = result.sort_values(
    by="Final_Score",
    ascending=False
)


# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

print()
print("=" * 80)
print("FINAL ROUTE SCORES")
print("=" * 80)

print(result.to_string(index=False))


# --------------------------------------------------
# SAVE
# --------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 80)
print("RESULT SAVED")
print("=" * 80)

print(OUTPUT_FILE)