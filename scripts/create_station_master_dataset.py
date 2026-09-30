import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION CANDIDATE MASTER DATASET
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"
RESULTS = BASE / "data" / "results"


# ============================================================
# INPUT FILES
# ============================================================

STATION_FILE = (
    PROCESSED /
    "station_candidates_final.gpkg"
)

HIGHWAY_FILE = (
    PROCESSED /
    "station_highway_connectivity.gpkg"
)

EDUCATION_FILE = (
    RESULTS /
    "station_education.csv"
)


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_GPKG = (
    PROCESSED /
    "station_master_dataset.gpkg"
)

OUTPUT_CSV = (
    RESULTS /
    "station_master_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("STATION CANDIDATE MASTER DATASET")
print("=" * 80)


stations = gpd.read_file(
    STATION_FILE,
    layer="station_candidates"
)


highways = gpd.read_file(
    HIGHWAY_FILE,
    layer="station_highway_connectivity"
)


education = pd.read_csv(
    EDUCATION_FILE
)


print(
    f"Station candidates: {len(stations)}"
)

print(
    f"Highway records: {len(highways)}"
)

print(
    f"Education records: {len(education)}"
)


# ============================================================
# VALIDATE UNIQUE IDS
# ============================================================

if not stations["candidate_id"].is_unique:

    raise ValueError(
        "Duplicate candidate_id values found "
        "in station candidates."
    )


if not highways["candidate_id"].is_unique:

    raise ValueError(
        "Duplicate candidate_id values found "
        "in highway dataset."
    )


if not education["candidate_id"].is_unique:

    raise ValueError(
        "Duplicate candidate_id values found "
        "in education dataset."
    )


# ============================================================
# SELECT HIGHWAY COLUMNS
# ============================================================

highway_columns = [
    "candidate_id",
    "highways_within_500m",
    "highways_within_1km",
    "highways_within_5km",
    "nearest_highway_distance_m",
    "nearest_highway_distance_km",
    "nearest_highway",
    "nearest_highway_type",
    "nearest_highway_state",
    "highway_within_500m",
    "highway_within_1km",
    "highway_within_5km",
]


highway_data = highways[
    highway_columns
].copy()


# ============================================================
# SELECT EDUCATION COLUMNS
# ============================================================

education_columns = [
    "candidate_id",
    "education_within_1km",
    "schools_within_1km",
    "colleges_within_1km",
    "universities_within_1km",
    "nearest_education_distance_m",
    "nearest_education_distance_km",
    "nearest_education_name",
    "nearest_education_type",
]


education_data = education[
    education_columns
].copy()


# ============================================================
# SELECT BASE STATION COLUMNS
# ============================================================

station_columns = [
    "candidate_id",
    "route",
    "candidate_type",
    "chainage_m",
    "chainage_km",
    "distance_from_end_km",
    "latitude",
    "longitude",
    "geometry",
]


master = stations[
    station_columns
].copy()


# ============================================================
# MERGE HIGHWAY DATA
# ============================================================

master = master.merge(
    highway_data,
    on="candidate_id",
    how="left",
    validate="one_to_one"
)


# ============================================================
# MERGE EDUCATION DATA
# ============================================================

master = master.merge(
    education_data,
    on="candidate_id",
    how="left",
    validate="one_to_one"
)


# ============================================================
# VALIDATE ROW COUNT
# ============================================================

if len(master) != len(stations):

    raise ValueError(
        "Row count changed after merging datasets."
    )


# ============================================================
# ROUND NUMERIC VALUES
# ============================================================

numeric_columns = [
    "chainage_m",
    "chainage_km",
    "distance_from_end_km",
    "latitude",
    "longitude",
    "nearest_highway_distance_m",
    "nearest_highway_distance_km",
    "nearest_education_distance_m",
    "nearest_education_distance_km",
]


for column in numeric_columns:

    if column in master.columns:

        master[column] = master[column].round(6)


# ============================================================
# SORT
# ============================================================

master = master.sort_values(
    [
        "route",
        "chainage_km"
    ]
).reset_index(
    drop=True
)


# ============================================================
# SAVE CSV
# ============================================================

RESULTS.mkdir(
    parents=True,
    exist_ok=True
)

csv_master = master.drop(
    columns="geometry"
)

csv_master.to_csv(
    OUTPUT_CSV,
    index=False
)


# ============================================================
# SAVE GEOPACKAGE
# ============================================================

if OUTPUT_GPKG.exists():

    OUTPUT_GPKG.unlink()


master.to_file(
    OUTPUT_GPKG,
    layer="station_master",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("MASTER DATASET SUMMARY")
print("=" * 80)


summary = (
    master
    .groupby("route")
    .agg(
        candidates=(
            "candidate_id",
            "count"
        ),

        education_candidates=(
            "education_within_1km",
            lambda x: (x > 0).sum()
        ),

        highway_500m_candidates=(
            "highway_within_500m",
            "sum"
        ),

        highway_1km_candidates=(
            "highway_within_1km",
            "sum"
        ),

        highway_5km_candidates=(
            "highway_within_5km",
            "sum"
        )
    )
    .reset_index()
)


print(
    summary.to_string(
        index=False
    )
)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 80)
print("VALIDATION")
print("=" * 80)


print(
    "Expected candidates:",
    len(stations)
)

print(
    "Final candidates:",
    len(master)
)

print(
    "Columns:",
    len(master.columns)
)

print(
    "CRS:",
    master.crs
)


if len(master) == 479:

    print(
        "\n479 station candidates preserved."
    )

else:

    print(
        "\nWARNING: candidate count is not 479."
    )


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 80)
print("OUTPUT")
print("=" * 80)

print(
    "CSV:"
)

print(
    OUTPUT_CSV
)

print(
    "\nGeoPackage:"
)

print(
    OUTPUT_GPKG
)

print(
    "\nStation master dataset created successfully."
)