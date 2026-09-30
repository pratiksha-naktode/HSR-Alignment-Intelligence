import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# TOPSIS ANALYSIS
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
    RESULTS / "topsis_route_results.csv"
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

if not NORMALIZED_FILE.exists():
    raise FileNotFoundError(
        f"Normalized file not found:\n{NORMALIZED_FILE}"
    )

if not AHP_FILE.exists():
    raise FileNotFoundError(
        f"AHP weights file not found:\n{AHP_FILE}"
    )


normalized = pd.read_csv(
    NORMALIZED_FILE
)

weights_df = pd.read_csv(
    AHP_FILE
)


# ============================================================
# VALIDATE
# ============================================================

missing_columns = [
    col for col in criteria
    if col not in normalized.columns
]

if missing_columns:
    raise ValueError(
        f"Missing normalized criteria: {missing_columns}"
    )


if len(weights_df) != 9:
    raise ValueError(
        "AHP weights file must contain exactly 9 criteria."
    )


weights = weights_df["weight"].to_numpy(
    dtype=float
)


if not np.isclose(
    weights.sum(),
    1.0,
    atol=1e-6
):
    raise ValueError(
        f"AHP weights do not sum to 1. Sum = {weights.sum()}"
    )


# ============================================================
# NORMALIZED MATRIX
# ============================================================

matrix = normalized[
    criteria
].to_numpy(
    dtype=float
)


# ============================================================
# APPLY AHP WEIGHTS
# ============================================================

weighted_matrix = (
    matrix * weights
)


weighted_df = pd.DataFrame(
    weighted_matrix,
    columns=criteria
)


# ============================================================
# IDEAL SOLUTIONS
# ============================================================
#
# IMPORTANT:
#
# The normalized scores already represent:
# higher score = better
#
# Therefore:
#
# Positive Ideal = maximum score
# Negative Ideal = minimum score
# ============================================================

positive_ideal = weighted_matrix.max(
    axis=0
)

negative_ideal = weighted_matrix.min(
    axis=0
)


# ============================================================
# DISTANCE FROM IDEAL SOLUTIONS
# ============================================================

distance_positive = np.sqrt(
    np.sum(
        (
            weighted_matrix
            - positive_ideal
        ) ** 2,
        axis=1
    )
)


distance_negative = np.sqrt(
    np.sum(
        (
            weighted_matrix
            - negative_ideal
        ) ** 2,
        axis=1
    )
)


# ============================================================
# TOPSIS CLOSENESS COEFFICIENT
# ============================================================

denominator = (
    distance_positive
    + distance_negative
)

closeness = np.divide(
    distance_negative,
    denominator,
    out=np.zeros_like(distance_negative),
    where=denominator != 0
)


# ============================================================
# RESULTS
# ============================================================

results = pd.DataFrame({
    "route": normalized["route"],
    "distance_to_positive_ideal": distance_positive,
    "distance_to_negative_ideal": distance_negative,
    "topsis_score": closeness,
})


results["rank"] = (
    results["topsis_score"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


results = results.sort_values(
    "rank"
)


# ============================================================
# DISPLAY
# ============================================================

print("=" * 80)
print("TOPSIS ROUTE ANALYSIS")
print("=" * 80)

print("\nAHP WEIGHTS")
print("-" * 80)

for criterion, weight in zip(
    criteria,
    weights
):

    print(
        f"{criterion:<15} {weight:.4f}"
    )


print("\n" + "=" * 80)
print("POSITIVE IDEAL SOLUTION")
print("=" * 80)

for criterion, value in zip(
    criteria,
    positive_ideal
):

    print(
        f"{criterion:<15} {value:.6f}"
    )


print("\n" + "=" * 80)
print("NEGATIVE IDEAL SOLUTION")
print("=" * 80)

for criterion, value in zip(
    criteria,
    negative_ideal
):

    print(
        f"{criterion:<15} {value:.6f}"
    )


print("\n" + "=" * 80)
print("TOPSIS RESULTS")
print("=" * 80)

print(
    results.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

results.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 80)
print("TOPSIS RESULTS SAVED")
print("=" * 80)

print(OUTPUT_FILE)