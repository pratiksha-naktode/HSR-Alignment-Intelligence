import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION CANDIDATE GENERATION
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"

INPUT_FILE = (
    PROCESSED /
    "route_chainage_points.gpkg"
)

OUTPUT_FILE = (
    PROCESSED /
    "station_candidates.gpkg"
)


# ============================================================
# SETTINGS
# ============================================================

# Candidate spacing along route
CANDIDATE_INTERVAL_KM = 5.0

# Source chainage points were generated every 1 km
SOURCE_INTERVAL_KM = 1.0


# ============================================================
# LOAD CHAINAGE
# ============================================================

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Chainage file not found:\n{INPUT_FILE}"
    )


print("=" * 80)
print("STATION CANDIDATE GENERATION")
print("=" * 80)

chainage = gpd.read_file(
    INPUT_FILE,
    layer="route_chainage"
)


if chainage.empty:

    raise ValueError(
        "Chainage dataset is empty."
    )


required_columns = [
    "route",
    "chainage_km",
    "distance_from_end_km",
    "latitude",
    "longitude",
    "geometry",
]


for column in required_columns:

    if column not in chainage.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


# ============================================================
# GENERATE CANDIDATES
# ============================================================

candidate_groups = []


for route_name, route_data in chainage.groupby(
    "route"
):

    route_data = route_data.sort_values(
        "chainage_km"
    ).copy()

    # --------------------------------------------------------
    # Select approximately every 5 km
    # --------------------------------------------------------

    target_chainages = []

    route_length = (
        route_data["chainage_km"].max()
    )

    current_chainage = 0.0

    while current_chainage <= route_length:

        target_chainages.append(
            current_chainage
        )

        current_chainage += (
            CANDIDATE_INTERVAL_KM
        )

    # --------------------------------------------------------
    # Find nearest actual chainage point
    # --------------------------------------------------------

    selected_indices = []

    for target in target_chainages:

        differences = (
            route_data["chainage_km"]
            - target
        ).abs()

        nearest_index = (
            differences.idxmin()
        )

        selected_indices.append(
            nearest_index
        )

    # Remove duplicates
    selected_indices = list(
        dict.fromkeys(
            selected_indices
        )
    )

    candidates = route_data.loc[
        selected_indices
    ].copy()

    # --------------------------------------------------------
    # Candidate metadata
    # --------------------------------------------------------

    candidates[
        "candidate_type"
    ] = "Station Candidate"

    candidates[
        "candidate_id"
    ] = [
        f"{route_name.replace(' ', '_')}_ST_{i:03d}"
        for i in range(
            1,
            len(candidates) + 1
        )
    ]

    candidates[
        "target_spacing_km"
    ] = CANDIDATE_INTERVAL_KM

    candidates[
        "source_chainage_interval_km"
    ] = SOURCE_INTERVAL_KM

    # --------------------------------------------------------
    # Calculate distance from ideal target
    # --------------------------------------------------------

    candidates[
        "target_chainage_error_km"
    ] = (
        candidates["chainage_km"]
        % CANDIDATE_INTERVAL_KM
    )

    # Better absolute distance to nearest 5 km
    candidates[
        "target_chainage_error_km"
    ] = candidates[
        "target_chainage_error_km"
    ].apply(
        lambda x: min(
            x,
            CANDIDATE_INTERVAL_KM - x
        )
    )

    candidate_groups.append(
        candidates
    )


# ============================================================
# COMBINE
# ============================================================

candidates = gpd.GeoDataFrame(
    pd.concat(
        candidate_groups,
        ignore_index=True
    ),
    crs=chainage.crs
)


# ============================================================
# CLEAN COLUMN ORDER
# ============================================================

columns = [
    "candidate_id",
    "route",
    "candidate_type",
    "chainage_m",
    "chainage_km",
    "distance_from_end_km",
    "latitude",
    "longitude",
    "target_spacing_km",
    "source_chainage_interval_km",
    "target_chainage_error_km",
    "geometry",
]


candidates = candidates[
    columns
]


# ============================================================
# ROUND VALUES
# ============================================================

numeric_columns = [
    "chainage_m",
    "chainage_km",
    "distance_from_end_km",
    "latitude",
    "longitude",
    "target_spacing_km",
    "source_chainage_interval_km",
    "target_chainage_error_km",
]


candidates[
    numeric_columns
] = candidates[
    numeric_columns
].round(6)


# ============================================================
# REMOVE OLD OUTPUT
# ============================================================

if OUTPUT_FILE.exists():

    OUTPUT_FILE.unlink()


# ============================================================
# SAVE
# ============================================================

candidates.to_file(
    OUTPUT_FILE,
    layer="station_candidates",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("STATION CANDIDATE SUMMARY")
print("=" * 80)

summary = (
    candidates
    .groupby("route")
    .agg(
        candidates=(
            "candidate_id",
            "count"
        ),
        first_chainage_km=(
            "chainage_km",
            "min"
        ),
        last_chainage_km=(
            "chainage_km",
            "max"
        ),
    )
    .reset_index()
)


print(
    summary.to_string(
        index=False
    )
)


print("\nTotal candidates:")
print(
    len(candidates)
)


print("\nOutput:")
print(
    OUTPUT_FILE
)


print("\nCRS:")
print(
    candidates.crs
)


print(
    "\nStation candidate layer created successfully."
)