import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = (
    BASE
    / "data"
    / "results"
    / "route_comparison_raw.csv"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "normalized_route_criteria.csv"
)

df = pd.read_csv(INPUT)


# ================================================================
# NORMALIZATION FUNCTIONS
# ================================================================

def normalize_cost(series):
    """
    Cost criterion:
    lower raw value = better normalized score
    """

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(1.0, index=series.index)

    return (maximum - series) / (maximum - minimum)


def normalize_benefit(series):
    """
    Benefit criterion:
    higher raw value = better normalized score
    """

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(1.0, index=series.index)

    return (series - minimum) / (maximum - minimum)


# ================================================================
# CURRENT 9 CRITERIA
# ================================================================

criteria = {
    "C1": ("forest_area_km2", "Cost"),
    "C2": ("agriculture_area_km2", "Cost"),
    "C3": ("built_up_area_km2", "Cost"),
    "C4": ("educational_sector_count", "Cost"),
    "C5": ("wetland_area_km2", "Cost"),
    "C6": ("waterbody_intersection_count", "Cost"),
    "C7": ("nearest_esz_distance_km", "Benefit"),
    "C8": ("route_length_km", "Cost"),
    "C9": ("highway_total_intersections", "Cost"),
}


# ================================================================
# CHECK FOR MISSING CRITERIA
# ================================================================

print()
print("=" * 80)
print("CRITERION AVAILABILITY CHECK")
print("=" * 80)

pending = []

for code, (column, criterion_type) in criteria.items():

    if column not in df.columns:
        pending.append((code, column))
        print(f"{code}: MISSING COLUMN -> {column}")
        continue

    missing_count = df[column].isna().sum()

    if missing_count > 0:
        pending.append((code, column))
        print(
            f"{code}: PENDING -> {column} "
            f"({missing_count} missing values)"
        )
    else:
        print(f"{code}: READY -> {column}")


# ================================================================
# DO NOT CREATE FINAL NORMALIZATION WITH MISSING CRITERIA
# ================================================================

if pending:

    print()
    print("=" * 80)
    print("NORMALIZATION STOPPED")
    print("=" * 80)

    print(
        "\nThe following criteria are still unresolved:"
    )

    for code, column in pending:
        print(f" - {code}: {column}")

    print()
    print(
        "C1-C3 LULC values must be available before "
        "the complete 9-criterion normalization matrix "
        "can be generated."
    )

    print()
    print(
        "No final normalized matrix has been generated."
    )

else:

    # ============================================================
    # NORMALIZE ALL NINE CRITERIA
    # ============================================================

    for code, (column, criterion_type) in criteria.items():

        score_column = f"{code}_score"

        if criterion_type == "Cost":
            df[score_column] = normalize_cost(
                df[column]
            )

        elif criterion_type == "Benefit":
            df[score_column] = normalize_benefit(
                df[column]
            )

    normalized_columns = [
        "route"
    ] + [
        f"{code}_score"
        for code in criteria
    ]

    normalized = df[
        normalized_columns
    ].copy()

    normalized.iloc[:, 1:] = (
        normalized.iloc[:, 1:]
        .round(4)
    )

    print()
    print("=" * 80)
    print("NORMALIZED 9-CRITERION MATRIX")
    print("=" * 80)

    print(
        normalized.to_string(index=False)
    )

    print()
    print("=" * 80)
    print("NORMALIZATION RANGE CHECK")
    print("=" * 80)

    for column in normalized.columns[1:]:

        print(
            column,
            "min =",
            normalized[column].min(),
            "max =",
            normalized[column].max()
        )

    df.to_csv(
        OUTPUT,
        index=False
    )

    print()
    print("Saved to:")
    print(OUTPUT)