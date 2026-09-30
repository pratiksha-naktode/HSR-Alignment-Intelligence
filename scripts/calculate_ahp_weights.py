import numpy as np
import pandas as pd
from pathlib import Path


BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

OUTPUT_FILE = RESULTS / "ahp_weights.csv"


# ============================================================
# 9 CRITERIA
# ============================================================

criteria = [
    "Forest Area",
    "Agriculture Area",
    "Built-up Area",
    "Educational Sector",
    "Wetland Impact",
    "Waterbody Impact",
    "ESZ Impact",
    "Route Length",
    "Highway Impact",
]


# ============================================================
# AHP PAIRWISE COMPARISON MATRIX
#
# Saaty scale:
# 1 = Equal importance
# 3 = Moderate importance
# 5 = Strong importance
# 7 = Very strong importance
# 9 = Extreme importance
#
# Reciprocal values are used automatically.
# ============================================================

matrix = np.array([

    # Forest Agriculture Built-up Education Wetland Waterbody ESZ Route Highway

    [1,   2,   2,   3,   1,   2,   1,   2,   2],   # Forest

    [1/2, 1,   1,   2,   1/2, 2,   1/2, 1,   2],   # Agriculture

    [1/2, 1,   1,   2,   1/2, 2,   1/2, 1,   1],   # Built-up

    [1/3, 1/2, 1/2, 1,   1/3, 1,   1/2, 1/2, 1], # Education

    [1,   2,   2,   3,   1,   3,   2,   2,   3],   # Wetland

    [1/2, 1/2, 1/2, 1,   1/3, 1,   1/2, 1,   1],   # Waterbody

    [1,   2,   2,   2,   1/2, 2,   1,   2,   2],   # ESZ

    [1/2, 1,   1,   2,   1/2, 1,   1/2, 1,   1],   # Route Length

    [1/2, 1/2, 1,   1,   1/3, 1,   1/2, 1,   1],   # Highway

], dtype=float)


# ============================================================
# VALIDATE MATRIX
# ============================================================

if matrix.shape != (9, 9):
    raise ValueError("AHP matrix must be 9 x 9")

if not np.allclose(np.diag(matrix), 1):
    raise ValueError("Diagonal values must be 1")

if not np.allclose(matrix * matrix.T, 1):
    raise ValueError("AHP matrix is not reciprocal")


# ============================================================
# PRINT MATRIX
# ============================================================

df_matrix = pd.DataFrame(
    matrix,
    index=criteria,
    columns=criteria
)

print("=" * 100)
print("AHP 9 × 9 PAIRWISE COMPARISON MATRIX")
print("=" * 100)

print(df_matrix.round(4).to_string())


# ============================================================
# CALCULATE PRIORITY VECTOR
# GEOMETRIC MEAN METHOD
# ============================================================

geometric_means = np.prod(matrix, axis=1) ** (1 / len(criteria))

weights = (
    geometric_means /
    geometric_means.sum()
)


# ============================================================
# CONSISTENCY CALCULATION
# ============================================================

weighted_sum = matrix @ weights

lambda_values = weighted_sum / weights

lambda_max = np.mean(lambda_values)

n = len(criteria)

consistency_index = (
    lambda_max - n
) / (n - 1)


# Random Index values
RI = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}


random_index = RI[n]

consistency_ratio = (
    consistency_index /
    random_index
)


# ============================================================
# OUTPUT WEIGHTS
# ============================================================

print("\n" + "=" * 100)
print("AHP WEIGHTS")
print("=" * 100)

for criterion, weight in zip(criteria, weights):

    print(
        f"{criterion:<25} {weight:.4f}"
    )


print("\n" + "=" * 100)
print("CONSISTENCY CHECK")
print("=" * 100)

print(
    f"Lambda max: {lambda_max:.4f}"
)

print(
    f"Consistency Index: {consistency_index:.4f}"
)

print(
    f"Consistency Ratio: {consistency_ratio:.4f}"
)


if consistency_ratio <= 0.10:

    print(
        "Consistency: ACCEPTABLE"
    )

else:

    print(
        "Consistency: NOT ACCEPTABLE"
    )


# ============================================================
# SAVE WEIGHTS
# ============================================================

weights_df = pd.DataFrame({
    "criterion": criteria,
    "weight": weights,
})

weights_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nWeights saved to:")
print(OUTPUT_FILE)