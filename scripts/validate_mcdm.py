import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

FINAL_FILE = RESULTS / "final_route_scores.csv"
WEIGHTS_FILE = RESULTS / "ahp_weights.csv"
NORMALIZED_FILE = RESULTS / "normalized_route_criteria.csv"


# --------------------------------------------------
# LOAD FILES
# --------------------------------------------------

final_df = pd.read_csv(FINAL_FILE)
weights_df = pd.read_csv(WEIGHTS_FILE)
normalized_df = pd.read_csv(NORMALIZED_FILE)


print("=" * 80)
print("MCDM VALIDATION")
print("=" * 80)


# --------------------------------------------------
# 1. CHECK AHP WEIGHTS
# --------------------------------------------------

print()
print("1. AHP WEIGHT VALIDATION")
print("-" * 80)

weight_sum = weights_df["weight"].sum()

print(f"Weight sum: {weight_sum:.6f}")

if np.isclose(weight_sum, 1.0):
    print("PASS: AHP weights sum to 1.")
else:
    print("FAIL: AHP weights do not sum to 1.")


# --------------------------------------------------
# 2. CHECK NORMALIZED VALUES
# --------------------------------------------------

print()
print("2. NORMALIZATION VALIDATION")
print("-" * 80)

score_columns = [
    "C1_highway_score",
    "C2_waterbody_score",
    "C3_wetland_score",
    "C4_esz_score"
]

for column in score_columns:

    minimum = normalized_df[column].min()
    maximum = normalized_df[column].max()

    print(
        f"{column:<25} "
        f"Min = {minimum:.6f}, "
        f"Max = {maximum:.6f}"
    )

    if minimum >= 0 and maximum <= 1:
        print("PASS")
    else:
        print("FAIL")


# --------------------------------------------------
# 3. VERIFY FINAL SCORE CALCULATION
# --------------------------------------------------

print()
print("3. FINAL SCORE VALIDATION")
print("-" * 80)

weights = dict(
    zip(
        weights_df["criterion"],
        weights_df["weight"]
    )
)

expected_scores = (
    final_df["C1_highway_score"]
    * weights["Highway Impact"]
    +
    final_df["C2_waterbody_score"]
    * weights["Waterbody Impact"]
    +
    final_df["C3_wetland_score"]
    * weights["Wetland Impact"]
    +
    final_df["C4_esz_score"]
    * weights["ESZ Impact"]
)

difference = (
    expected_scores - final_df["Final_Score"]
).abs()

print("Maximum calculation difference:",
      f"{difference.max():.10f}")

if difference.max() < 1e-9:
    print("PASS: Final scores are calculated correctly.")
else:
    print("FAIL: Final score calculation mismatch.")


# --------------------------------------------------
# 4. CHECK CONTRIBUTION SUM
# --------------------------------------------------

print()
print("4. CONTRIBUTION VALIDATION")
print("-" * 80)

contribution_columns = [
    "Highway_Contribution",
    "Waterbody_Contribution",
    "Wetland_Contribution",
    "ESZ_Contribution"
]

contribution_sum = final_df[contribution_columns].sum(axis=1)

contribution_difference = (
    contribution_sum - final_df["Final_Score"]
).abs()

for i, row in final_df.iterrows():

    print(
        f"{row['route']:<10} "
        f"Contribution Sum = {contribution_sum.iloc[i]:.6f} | "
        f"Final Score = {row['Final_Score']:.6f}"
    )

if contribution_difference.max() < 1e-9:
    print("PASS: Contributions correctly sum to final scores.")
else:
    print("FAIL: Contribution mismatch.")


# --------------------------------------------------
# 5. ROUTE ORDERING
# --------------------------------------------------

print()
print("5. ROUTE SCORE ORDER")
print("-" * 80)

ranking = final_df.sort_values(
    by="Final_Score",
    ascending=False
).reset_index(drop=True)

for i, row in ranking.iterrows():

    print(
        f"{i + 1}. {row['route']} "
        f"-> {row['Final_Score']:.6f}"
    )


# --------------------------------------------------
# 6. CHECK FOR MISSING VALUES
# --------------------------------------------------

print()
print("6. MISSING VALUE CHECK")
print("-" * 80)

missing = final_df.isnull().sum().sum()

print("Total missing values:", missing)

if missing == 0:
    print("PASS: No missing values.")
else:
    print("FAIL: Missing values detected.")


# --------------------------------------------------
# FINAL STATUS
# --------------------------------------------------

all_checks = [
    np.isclose(weight_sum, 1.0),
    all(
        normalized_df[column].min() >= 0
        and normalized_df[column].max() <= 1
        for column in score_columns
    ),
    difference.max() < 1e-9,
    contribution_difference.max() < 1e-9,
    missing == 0
]

print()
print("=" * 80)

if all(all_checks):
    print("OVERALL VALIDATION: PASS")
    print("AHP + Normalization + MCDM pipeline is internally consistent.")
else:
    print("OVERALL VALIDATION: REVIEW REQUIRED")

print("=" * 80)