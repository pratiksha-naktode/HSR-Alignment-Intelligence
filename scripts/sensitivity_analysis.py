import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

NORMALIZED_FILE = RESULTS / "normalized_route_criteria.csv"
WEIGHTS_FILE = RESULTS / "ahp_weights.csv"

OUTPUT_FILE = RESULTS / "sensitivity_analysis.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

normalized = pd.read_csv(NORMALIZED_FILE)
weights_df = pd.read_csv(WEIGHTS_FILE)


# --------------------------------------------------
# BASELINE AHP WEIGHTS
# --------------------------------------------------

base_weights = dict(
    zip(
        weights_df["criterion"],
        weights_df["weight"]
    )
)

w = np.array([
    base_weights["Highway Impact"],
    base_weights["Waterbody Impact"],
    base_weights["Wetland Impact"],
    base_weights["ESZ Impact"]
])


# --------------------------------------------------
# NORMALIZED CRITERIA MATRIX
# --------------------------------------------------

scores = normalized[
    [
        "C1_highway_score",
        "C2_waterbody_score",
        "C3_wetland_score",
        "C4_esz_score"
    ]
].values


# --------------------------------------------------
# SENSITIVITY SCENARIOS
#
# Each scenario changes the importance of ONE
# criterion while keeping the other criteria
# proportionally adjusted.
# --------------------------------------------------

scenarios = {
    "Baseline": w,

    "Highway +10%": w * np.array([
        1.10, 1.0, 1.0, 1.0
    ]),

    "Waterbody +10%": w * np.array([
        1.0, 1.10, 1.0, 1.0
    ]),

    "Wetland +10%": w * np.array([
        1.0, 1.0, 1.10, 1.0
    ]),

    "ESZ +10%": w * np.array([
        1.0, 1.0, 1.0, 1.10
    ]),

    "Highway +20%": w * np.array([
        1.20, 1.0, 1.0, 1.0
    ]),

    "Waterbody +20%": w * np.array([
        1.0, 1.20, 1.0, 1.0
    ]),

    "Wetland +20%": w * np.array([
        1.0, 1.0, 1.20, 1.0
    ]),

    "ESZ +20%": w * np.array([
        1.0, 1.0, 1.0, 1.20
    ])
}


# --------------------------------------------------
# CALCULATE SCENARIOS
# --------------------------------------------------

results = []

for scenario_name, scenario_weights in scenarios.items():

    # Normalize weights so they always sum to 1
    scenario_weights = (
        scenario_weights / scenario_weights.sum()
    )

    route_scores = scores @ scenario_weights

    for i, route in enumerate(normalized["route"]):

        results.append({
            "Scenario": scenario_name,
            "Route": route,
            "Highway_Weight": scenario_weights[0],
            "Waterbody_Weight": scenario_weights[1],
            "Wetland_Weight": scenario_weights[2],
            "ESZ_Weight": scenario_weights[3],
            "Final_Score": route_scores[i]
        })


# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

result_df = pd.DataFrame(results)


# --------------------------------------------------
# ADD RANK
# --------------------------------------------------

result_df["Rank"] = (
    result_df
    .groupby("Scenario")["Final_Score"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("=" * 100)
print("SENSITIVITY ANALYSIS")
print("=" * 100)

print()

for scenario in scenarios:

    scenario_result = result_df[
        result_df["Scenario"] == scenario
    ].sort_values(
        by="Final_Score",
        ascending=False
    )

    print("-" * 100)
    print(scenario)

    for _, row in scenario_result.iterrows():

        print(
            f"{int(row['Rank'])}. "
            f"{row['Route']:<10} "
            f"Score = {row['Final_Score']:.6f}"
        )


# --------------------------------------------------
# SAVE COMPLETE RESULTS
# --------------------------------------------------

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# SUMMARY TABLE
# --------------------------------------------------

summary = result_df.pivot(
    index="Scenario",
    columns="Route",
    values="Final_Score"
)

print()
print("=" * 100)
print("SENSITIVITY SUMMARY")
print("=" * 100)

print(
    summary.round(6).to_string()
)


# --------------------------------------------------
# RANKING STABILITY
# --------------------------------------------------

print()
print("=" * 100)
print("RANKING STABILITY")
print("=" * 100)

top_routes = (
    result_df[
        result_df["Rank"] == 1
    ]
    .groupby("Route")
    .size()
    .sort_values(
        ascending=False
    )
)

print(top_routes)


print()
print("=" * 100)
print("RESULT SAVED")
print("=" * 100)

print(OUTPUT_FILE)