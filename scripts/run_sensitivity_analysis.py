import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# TOPSIS SENSITIVITY ANALYSIS
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

RESULTS = BASE / "data" / "results"

NORMALIZED_FILE = (
    RESULTS / "normalized_route_criteria.csv"
)

AHP_FILE = (
    RESULTS / "ahp_weights.csv"
)

OUTPUT_FILE = (
    RESULTS / "topsis_sensitivity_results.csv"
)


# ============================================================
# CRITERIA
# ============================================================

criteria = [
    "C1_score",
    "C2_score",
    "C3_score",
    "C4_score",
    "C5_score",
    "C6_score",
    "C7_score",
    "C8_score",
    "C9_score",
]


# ============================================================
# LOAD DATA
# ============================================================

normalized = pd.read_csv(
    NORMALIZED_FILE
)

ahp = pd.read_csv(
    AHP_FILE
)

matrix = normalized[
    criteria
].to_numpy(dtype=float)

base_weights = ahp[
    "weight"
].to_numpy(dtype=float)


# ============================================================
# VALIDATION
# ============================================================

if matrix.shape[1] != 9:
    raise ValueError(
        "Expected exactly 9 normalized criteria."
    )

if len(base_weights) != 9:
    raise ValueError(
        "Expected exactly 9 AHP weights."
    )

if not np.isclose(
    base_weights.sum(),
    1.0,
    atol=1e-6
):
    raise ValueError(
        "AHP weights must sum to 1."
    )


# ============================================================
# TOPSIS FUNCTION
# ============================================================

def calculate_topsis(matrix, weights):

    weighted = matrix * weights

    positive_ideal = weighted.max(
        axis=0
    )

    negative_ideal = weighted.min(
        axis=0
    )

    distance_positive = np.sqrt(
        np.sum(
            (
                weighted
                - positive_ideal
            ) ** 2,
            axis=1
        )
    )

    distance_negative = np.sqrt(
        np.sum(
            (
                weighted
                - negative_ideal
            ) ** 2,
            axis=1
        )
    )

    denominator = (
        distance_positive
        + distance_negative
    )

    scores = np.divide(
        distance_negative,
        denominator,
        out=np.zeros_like(
            distance_negative
        ),
        where=denominator != 0
    )

    return scores


# ============================================================
# WEIGHT NORMALIZATION
# ============================================================

def normalize_weights(weights):

    weights = np.array(
        weights,
        dtype=float
    )

    return (
        weights / weights.sum()
    )


# ============================================================
# SCENARIO DEFINITIONS
# ============================================================

scenarios = {}


# ------------------------------------------------------------
# 1. BASELINE
# ------------------------------------------------------------

scenarios[
    "Baseline AHP"
] = base_weights.copy()


# ------------------------------------------------------------
# 2. EQUAL WEIGHTS
# ------------------------------------------------------------

scenarios[
    "Equal Weights"
] = np.ones(9) / 9


# ------------------------------------------------------------
# 3. ENVIRONMENTAL FOCUS
#
# Increase importance of:
# Forest, Wetland, ESZ
# ------------------------------------------------------------

weights = base_weights.copy()

for index in [0, 4, 6]:

    weights[index] *= 1.50

scenarios[
    "Environmental Focus"
] = normalize_weights(weights)


# ------------------------------------------------------------
# 4. AGRICULTURE FOCUS
# ------------------------------------------------------------

weights = base_weights.copy()

weights[1] *= 1.50

scenarios[
    "Agriculture Focus"
] = normalize_weights(weights)


# ------------------------------------------------------------
# 5. SOCIAL / DEVELOPMENT FOCUS
#
# Education + Built-up
# ------------------------------------------------------------

weights = base_weights.copy()

weights[2] *= 1.50
weights[3] *= 1.50

scenarios[
    "Social Development Focus"
] = normalize_weights(weights)


# ------------------------------------------------------------
# 6. INFRASTRUCTURE FOCUS
#
# Route Length + Highway
# ------------------------------------------------------------

weights = base_weights.copy()

weights[7] *= 1.50
weights[8] *= 1.50

scenarios[
    "Infrastructure Focus"
] = normalize_weights(weights)


# ------------------------------------------------------------
# 7. WATER / WETLAND FOCUS
# ------------------------------------------------------------

weights = base_weights.copy()

weights[4] *= 1.50
weights[5] *= 1.50

scenarios[
    "Water Environment Focus"
] = normalize_weights(weights)


# ------------------------------------------------------------
# 8. FOREST FOCUS
# ------------------------------------------------------------

weights = base_weights.copy()

weights[0] *= 2.00

scenarios[
    "Forest Focus"
] = normalize_weights(weights)


# ============================================================
# RUN SENSITIVITY ANALYSIS
# ============================================================

route_names = normalized[
    "route"
].tolist()

all_results = []

scenario_scores = {}


for scenario_name, weights in scenarios.items():

    scores = calculate_topsis(
        matrix,
        weights
    )

    scenario_scores[
        scenario_name
    ] = scores

    for route, score in zip(
        route_names,
        scores
    ):

        all_results.append({
            "scenario": scenario_name,
            "route": route,
            "topsis_score": score,
        })


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results = pd.DataFrame(
    all_results
)


# ============================================================
# ADD RANK WITHIN EACH SCENARIO
# ============================================================

results["rank"] = (
    results
    .groupby("scenario")[
        "topsis_score"
    ]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


# ============================================================
# SORT
# ============================================================

results = results.sort_values(
    [
        "scenario",
        "rank"
    ]
)


# ============================================================
# DISPLAY
# ============================================================

print("=" * 90)
print("TOPSIS SENSITIVITY ANALYSIS")
print("=" * 90)

for scenario_name in scenarios:

    print("\n" + "-" * 90)
    print(scenario_name)
    print("-" * 90)

    scenario_result = results[
        results["scenario"]
        == scenario_name
    ].sort_values(
        "rank"
    )

    print(
        scenario_result[
            [
                "route",
                "topsis_score",
                "rank"
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# WEIGHT COMPARISON
# ============================================================

print("\n" + "=" * 90)
print("SCENARIO WEIGHTS")
print("=" * 90)

weight_rows = []

for scenario_name, weights in scenarios.items():

    row = {
        "scenario": scenario_name
    }

    for criterion, weight in zip(
        criteria,
        weights
    ):

        row[criterion] = weight

    weight_rows.append(row)


weight_df = pd.DataFrame(
    weight_rows
)

print(
    weight_df.to_string(
        index=False
    )
)


# ============================================================
# ROUTE SCORE SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("ROUTE SCORE SUMMARY")
print("=" * 90)

score_pivot = results.pivot(
    index="scenario",
    columns="route",
    values="topsis_score"
)

print(
    score_pivot.round(6).to_string()
)


# ============================================================
# ROUTE POSITION SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("ROUTE POSITION SUMMARY")
print("=" * 90)

rank_pivot = results.pivot(
    index="scenario",
    columns="route",
    values="rank"
)

print(
    rank_pivot.to_string()
)


# ============================================================
# SAVE RESULTS
# ============================================================

results.to_csv(
    OUTPUT_FILE,
    index=False
)


weights_output = (
    RESULTS /
    "topsis_sensitivity_weights.csv"
)

weight_df.to_csv(
    weights_output,
    index=False
)


print("\n" + "=" * 90)
print("FILES SAVED")
print("=" * 90)

print(
    f"Sensitivity results:\n{OUTPUT_FILE}"
)

print(
    f"\nScenario weights:\n{weights_output}"
)

print("\nSensitivity analysis completed.")