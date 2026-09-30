import pandas as pd
import numpy as np
from pathlib import Path



# HSR ROUTE OPTIMIZATION  # FINAL DECISION DATASET

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

RESULTS = BASE / "data" / "results"


MASTER_FILE = RESULTS / "route_comparison_raw.csv"
NORMALIZED_FILE = RESULTS / "normalized_route_criteria.csv"
AHP_FILE = RESULTS / "ahp_weights.csv"
TOPSIS_FILE = RESULTS / "topsis_route_results.csv"

OUTPUT_FILE = (
    RESULTS / "final_route_decision_dataset.csv"
)



print("=" * 90)
print("CREATING FINAL ROUTE DECISION DATASET")
print("=" * 90)


master = pd.read_csv(
    MASTER_FILE
)

normalized = pd.read_csv(
    NORMALIZED_FILE
)

ahp = pd.read_csv(
    AHP_FILE
)

topsis = pd.read_csv(
    TOPSIS_FILE
)


# ============================================================
# CRITERION MAPPING
# ============================================================
#
# raw_name       = column in master CSV
# score_name     = column in normalized CSV
# ahp_name       = exact name in ahp_weights.csv
# display_name   = readable name in final dataset
#
# ============================================================

criterion_mapping = {

    "C1": {
        "raw_name": "forest_area_km2",
        "score_name": "C1_score",
        "ahp_name": "Forest Area",
        "display_name": "Forest Area",
    },

    "C2": {
        "raw_name": "agriculture_area_km2",
        "score_name": "C2_score",
        "ahp_name": "Agriculture Area",
        "display_name": "Agriculture Area",
    },

    "C3": {
        "raw_name": "built_up_area_km2",
        "score_name": "C3_score",
        "ahp_name": "Built-up Area",
        "display_name": "Built-up Area",
    },

    "C4": {
        "raw_name": "educational_sector_count",
        "score_name": "C4_score",
        "ahp_name": "Educational Sector",
        "display_name": "Educational Sector",
    },

    "C5": {
        "raw_name": "wetland_area_km2",
        "score_name": "C5_score",
        "ahp_name": "Wetland Impact",
        "display_name": "Wetland Impact",
    },

    "C6": {
        "raw_name": "waterbody_intersection_count",
        "score_name": "C6_score",
        "ahp_name": "Waterbody Impact",
        "display_name": "Bhuvan Waterbody Polygon Intersections",
    },

    "C7": {
        "raw_name": "nearest_esz_distance_km",
        "score_name": "C7_score",
        "ahp_name": "ESZ Impact",
        "display_name": "Nearest ESZ",
    },

    "C8": {
        "raw_name": "route_length_km",
        "score_name": "C8_score",
        "ahp_name": "Route Length",
        "display_name": "Route Length",
    },

    "C9": {
        "raw_name": "highway_total_intersections",
        "score_name": "C9_score",
        "ahp_name": "Highway Impact",
        "display_name": "Highway Intersection",
    },
}


# ============================================================
# BASIC FILE VALIDATION
# ============================================================

print("\nChecking input files...")


required_files = [
    MASTER_FILE,
    NORMALIZED_FILE,
    AHP_FILE,
    TOPSIS_FILE,
]

for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )


print("All required files found.")


# ============================================================
# VALIDATE MASTER DATASET
# ============================================================

if "route" not in master.columns:

    raise ValueError(
        "Master dataset is missing 'route' column."
    )


for criterion_code, item in criterion_mapping.items():

    column = item["raw_name"]

    if column not in master.columns:

        raise ValueError(
            f"{criterion_code}: Missing master column "
            f"'{column}'"
        )


# ============================================================
# VALIDATE NORMALIZED DATASET
# ============================================================

if "route" not in normalized.columns:

    raise ValueError(
        "Normalized dataset is missing 'route' column."
    )


for criterion_code, item in criterion_mapping.items():

    column = item["score_name"]

    if column not in normalized.columns:

        raise ValueError(
            f"{criterion_code}: Missing normalized column "
            f"'{column}'"
        )


# ============================================================
# VALIDATE AHP DATASET
# ============================================================

required_ahp_columns = [
    "criterion",
    "weight",
]

for column in required_ahp_columns:

    if column not in ahp.columns:

        raise ValueError(
            f"AHP weights file is missing '{column}' column."
        )


# Create dictionary from AHP file
ahp_weights = {}

for _, row in ahp.iterrows():

    criterion_name = str(
        row["criterion"]
    ).strip()

    weight = float(
        row["weight"]
    )

    ahp_weights[
        criterion_name
    ] = weight


print("\nAHP criteria found:")

for name, weight in ahp_weights.items():

    print(
        f"{name:<25} {weight:.6f}"
    )


# ============================================================
# VALIDATE ALL 9 AHP WEIGHTS
# ============================================================

print("\nChecking AHP weights...")

for criterion_code, item in criterion_mapping.items():

    ahp_name = item["ahp_name"]

    if ahp_name not in ahp_weights:

        raise ValueError(
            f"{criterion_code}: AHP weight missing for "
            f"'{ahp_name}'"
        )


# ============================================================
# VALIDATE TOPSIS DATASET
# ============================================================

required_topsis_columns = [
    "route",
    "distance_to_positive_ideal",
    "distance_to_negative_ideal",
    "topsis_score",
    "rank",
]

for column in required_topsis_columns:

    if column not in topsis.columns:

        raise ValueError(
            f"TOPSIS results are missing '{column}' column."
        )


# ============================================================
# BUILD FINAL DATASET
# ============================================================

final = master[
    ["route"]
].copy()


# ============================================================
# ADD RAW CRITERIA
# ============================================================

for criterion_code, item in criterion_mapping.items():

    final[
        f"{criterion_code}_{item['display_name']}_raw"
    ] = master[
        item["raw_name"]
    ]


# ============================================================
# NORMALIZED DATA LOOKUP
# ============================================================

normalized_lookup = (
    normalized
    .set_index("route")
)


# ============================================================
# ADD NORMALIZED SCORES
# ============================================================

for criterion_code, item in criterion_mapping.items():

    final[
        f"{criterion_code}_normalized"
    ] = final[
        "route"
    ].map(
        normalized_lookup[
            item["score_name"]
        ]
    )


# ============================================================
# CHECK NORMALIZED VALUES
# ============================================================

for criterion_code in criterion_mapping:

    column = f"{criterion_code}_normalized"

    if final[column].isna().any():

        missing_routes = final.loc[
            final[column].isna(),
            "route"
        ].tolist()

        raise ValueError(
            f"{criterion_code}: Missing normalized values "
            f"for routes: {missing_routes}"
        )


# ============================================================
# ADD AHP WEIGHTS
# ============================================================

for criterion_code, item in criterion_mapping.items():

    final[
        f"{criterion_code}_weight"
    ] = ahp_weights[
        item["ahp_name"]
    ]


# ============================================================
# VALIDATE WEIGHT SUM
# ============================================================

weight_columns = [
    f"C{i}_weight"
    for i in range(1, 10)
]

weight_sum = float(
    final[
        weight_columns
    ].iloc[0].sum()
)


print("\n" + "=" * 90)
print("AHP WEIGHT VALIDATION")
print("=" * 90)

print(
    f"Weight sum = {weight_sum:.8f}"
)


if not np.isclose(
    weight_sum,
    1.0,
    atol=1e-6
):

    raise ValueError(
        f"AHP weights do not sum to 1. "
        f"Current sum = {weight_sum}"
    )


print("AHP weights: VALID")


# ============================================================
# CALCULATE WEIGHTED SCORES
# ============================================================

for criterion_code in criterion_mapping:

    normalized_column = (
        f"{criterion_code}_normalized"
    )

    weight_column = (
        f"{criterion_code}_weight"
    )

    weighted_column = (
        f"{criterion_code}_weighted_score"
    )

    final[
        weighted_column
    ] = (
        final[
            normalized_column
        ]
        *
        final[
            weight_column
        ]
    )
# ============================================================
# ADD ENVIRONMENTAL INTERSECTION-LENGTH METRICS
# ============================================================

intersection_length_columns = [
    "forest_intersection_length_km",
    "agriculture_intersection_length_km",
    "builtup_intersection_length_km",
    "wetland_intersection_length_km",
    "waterbody_intersection_length_km",
]

for column in intersection_length_columns:

    if column not in master.columns:
        raise ValueError(
            f"Missing intersection-length column: {column}"
        )

    final[column] = final["route"].map(
        master.set_index("route")[column]
    )

print("\nEnvironmental intersection-length metrics: VALID")

# ============================================================
# TOPSIS LOOKUP
# ============================================================

topsis_lookup = (
    topsis
    .set_index("route")
)


# ============================================================
# ADD TOPSIS RESULTS
# ============================================================

final[
    "distance_to_positive_ideal"
] = final[
    "route"
].map(
    topsis_lookup[
        "distance_to_positive_ideal"
    ]
)


final[
    "distance_to_negative_ideal"
] = final[
    "route"
].map(
    topsis_lookup[
        "distance_to_negative_ideal"
    ]
)


final[
    "topsis_score"
] = final[
    "route"
].map(
    topsis_lookup[
        "topsis_score"
    ]
)


final[
    "topsis_rank"
] = final[
    "route"
].map(
    topsis_lookup[
        "rank"
    ]
)


# ============================================================
# TOPSIS VALIDATION
# ============================================================

if final[
    "topsis_score"
].isna().any():

    missing_routes = final.loc[
        final["topsis_score"].isna(),
        "route"
    ].tolist()

    raise ValueError(
        f"Missing TOPSIS scores for: {missing_routes}"
    )


if final[
    "topsis_rank"
].isna().any():

    missing_routes = final.loc[
        final["topsis_rank"].isna(),
        "route"
    ].tolist()

    raise ValueError(
        f"Missing TOPSIS ranks for: {missing_routes}"
    )


print("\n" + "=" * 90)
print("TOPSIS VALIDATION")
print("=" * 90)

print("TOPSIS scores: VALID")
print("TOPSIS ranks: VALID")


# ============================================================
# SORT BY TOPSIS RANK
# ============================================================

final = final.sort_values(
    "topsis_rank"
).reset_index(
    drop=True
)


# ============================================================
# ROUND NUMERIC VALUES
# ============================================================

numeric_columns = final.select_dtypes(
    include=np.number
).columns

final[
    numeric_columns
] = final[
    numeric_columns
].round(8)


# ============================================================
# FINAL ROUTE DECISION SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("FINAL ROUTE DECISION SUMMARY")
print("=" * 90)


summary_columns = [
    "route",

    "C1_Forest Area_raw",
    "C2_Agriculture Area_raw",
    "C3_Built-up Area_raw",
    "C4_Educational Sector_raw",
    "C5_Wetland Impact_raw",
    "C6_Bhuvan Waterbody Polygon Intersections_raw",
    "C7_Nearest ESZ_raw",
    "C8_Route Length_raw",
    "C9_Highway Intersection_raw",

    "topsis_score",
    "topsis_rank",
]


print(
    final[
        summary_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# WEIGHTED SCORE CHECK
# ============================================================

weighted_columns = [
    f"C{i}_weighted_score"
    for i in range(1, 10)
]

final[
    "weighted_score_total"
] = final[
    weighted_columns
].sum(
    axis=1
)


print("\n" + "=" * 90)
print("WEIGHTED SCORE CHECK")
print("=" * 90)

print(
    final[
        [
            "route",
            "weighted_score_total",
            "topsis_score",
            "topsis_rank",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

final.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 90)
print("FINAL DATASET SAVED")
print("=" * 90)

print(
    OUTPUT_FILE
)

print(
    f"\nRows: {len(final)}"
)

print(
    f"Columns: {len(final.columns)}"
)

print(
    "\nFinal decision dataset created successfully."
)