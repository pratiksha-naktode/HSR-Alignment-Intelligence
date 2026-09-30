import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION CANDIDATE SCREENING
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

INPUT = (
    BASE
    / "data"
    / "processed"
    / "station_gis_layer.gpkg"
)

OUTPUT = (
    BASE
    / "data"
    / "processed"
    / "station_screening.gpkg"
)

CSV_OUTPUT = (
    BASE
    / "data"
    / "results"
    / "station_screening.csv"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("STATION CANDIDATE SCREENING")
print("=" * 70)

gdf = gpd.read_file(
    INPUT,
    layer="station_gis"
)

print(
    f"Input candidates: {len(gdf)}"
)


# ============================================================
# EDUCATION ACCESS
# ============================================================

gdf["education_access"] = (
    gdf["education_1km"].fillna(0) > 0
)


# ============================================================
# HIGHWAY ACCESS
# ============================================================

gdf["highway_access_500m"] = (
    gdf["highways_500m"].fillna(0) > 0
)

gdf["highway_access_1km"] = (
    gdf["highways_1km"].fillna(0) > 0
)


# ============================================================
# FACTUAL ACCESS SUMMARY
# ============================================================

def classify_access(row):

    education = row["education_access"]
    highway = row["highway_access_1km"]

    if education and highway:
        return "Education + Highway"

    if education:
        return "Education Only"

    if highway:
        return "Highway Only"

    return "Limited Nearby Access"


gdf["access_summary"] = gdf.apply(
    classify_access,
    axis=1
)


# ============================================================
# EDUCATION DENSITY
# ============================================================

gdf["education_density_class"] = pd.cut(
    gdf["education_1km"].fillna(0),
    bins=[
        -1,
        0,
        5,
        15,
        float("inf")
    ],
    labels=[
        "None",
        "1-5",
        "6-15",
        "16+"
    ]
)


# ============================================================
# HIGHWAY PROXIMITY CLASS
# ============================================================

def highway_proximity(row):

    distance = row["nearest_highway_km"]

    if pd.isna(distance):
        return "No highway within 5 km"

    if distance <= 0.5:
        return "Within 500 m"

    if distance <= 1:
        return "500 m - 1 km"

    if distance <= 5:
        return "1 - 5 km"

    return "Beyond 5 km"


gdf["highway_proximity_class"] = gdf.apply(
    highway_proximity,
    axis=1
)


# ============================================================
# SORT
# ============================================================

gdf = gdf.sort_values(
    [
        "route",
        "chainage_km"
    ]
).reset_index(
    drop=True
)


# ============================================================
# SAVE GEOPACKAGE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

if OUTPUT.exists():
    OUTPUT.unlink()

gdf.to_file(
    OUTPUT,
    layer="station_screening",
    driver="GPKG"
)


# ============================================================
# SAVE CSV
# ============================================================

csv_gdf = gdf.drop(
    columns="geometry"
)

csv_gdf.to_csv(
    CSV_OUTPUT,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("SCREENING SUMMARY")
print("=" * 70)

print()

print(
    gdf.groupby(
        ["route", "access_summary"]
    )
    .size()
    .to_string()
)


print()
print("=" * 70)
print("VALIDATION")
print("=" * 70)

print(
    f"Input candidates: {len(gdf)}"
)

print(
    f"Unique candidate IDs: "
    f"{gdf['station_id'].nunique()}"
)

print(
    f"CRS: {gdf.crs}"
)


print()
print("=" * 70)
print("OUTPUT")
print("=" * 70)

print(
    OUTPUT
)

print(
    CSV_OUTPUT
)

print(
    "\nStation screening dataset created successfully."
)