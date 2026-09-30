import geopandas as gpd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION GIS LAYER
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

INPUT = (
    BASE
    / "data"
    / "processed"
    / "station_master_dataset.gpkg"
)

OUTPUT = (
    BASE
    / "data"
    / "processed"
    / "station_gis_layer.gpkg"
)


# ============================================================
# LOAD MASTER DATASET
# ============================================================

print("=" * 70)
print("CREATING STATION GIS LAYER")
print("=" * 70)

gdf = gpd.read_file(
    INPUT,
    layer="station_master"
)

print(
    f"Input candidates: {len(gdf)}"
)

print(
    f"Input CRS: {gdf.crs}"
)


# ============================================================
# SELECT MAP / POPUP FIELDS
# ============================================================

fields = [
    "candidate_id",
    "route",
    "candidate_type",

    "chainage_m",
    "chainage_km",
    "distance_from_end_km",

    "latitude",
    "longitude",

    # Education
    "education_within_1km",
    "schools_within_1km",
    "colleges_within_1km",
    "universities_within_1km",
    "nearest_education_distance_km",
    "nearest_education_name",
    "nearest_education_type",

    # Highway
    "highways_within_500m",
    "highways_within_1km",
    "highways_within_5km",
    "nearest_highway_distance_km",
    "nearest_highway",
    "nearest_highway_type",
    "nearest_highway_state",

    "highway_within_500m",
    "highway_within_1km",
    "highway_within_5km",

    "geometry",
]


gdf = gdf[fields].copy()


# ============================================================
# CREATE POPUP-FRIENDLY FIELD NAMES
# ============================================================

gdf = gdf.rename(
    columns={
        "candidate_id": "station_id",
        "candidate_type": "station_type",

        "chainage_m": "chainage_m",
        "chainage_km": "chainage_km",
        "distance_from_end_km": "distance_end_km",

        "education_within_1km": "education_1km",
        "schools_within_1km": "schools_1km",
        "colleges_within_1km": "colleges_1km",
        "universities_within_1km": "universities_1km",

        "nearest_education_distance_km":
            "nearest_education_km",

        "nearest_education_name":
            "nearest_education",

        "nearest_education_type":
            "nearest_education_type",

        "highways_within_500m":
            "highways_500m",

        "highways_within_1km":
            "highways_1km",

        "highways_within_5km":
            "highways_5km",

        "nearest_highway_distance_km":
            "nearest_highway_km",

        "nearest_highway":
            "nearest_highway",

        "nearest_highway_type":
            "nearest_highway_type",

        "nearest_highway_state":
            "nearest_highway_state",
    }
)


# ============================================================
# ENSURE WGS84
# ============================================================

if gdf.crs is None:

    gdf = gdf.set_crs(
        "EPSG:4326"
    )

elif gdf.crs.to_epsg() != 4326:

    gdf = gdf.to_crs(
        "EPSG:4326"
    )


# ============================================================
# SORT BY ROUTE AND CHAINAGE
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
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

if OUTPUT.exists():

    OUTPUT.unlink()


gdf.to_file(
    OUTPUT,
    layer="station_gis",
    driver="GPKG"
)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 70)
print("VALIDATION")
print("=" * 70)

print(
    f"Final station features: {len(gdf)}"
)

print(
    f"CRS: {gdf.crs}"
)

print(
    f"Fields: {len(gdf.columns)}"
)

print()

print(
    gdf.groupby("route")
    .size()
    .to_string()
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 70)
print("OUTPUT")
print("=" * 70)

print(
    OUTPUT
)

print(
    "\nStation GIS layer created successfully."
)