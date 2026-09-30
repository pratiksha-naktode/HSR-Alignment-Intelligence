import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION CANDIDATE - HIGHWAY CONNECTIVITY
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"
RESULTS = BASE / "data" / "results"

HIGHWAY_FILE = (
    Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT")
    / "ctiteria_dataset"
    / "GatiShakti_MORTH_National_Highways.geojsonl"
)

STATION_FILE = (
    PROCESSED / "station_candidates_final.gpkg"
)

OUTPUT_FILE = (
    PROCESSED / "station_highway_connectivity.gpkg"
)

CSV_FILE = (
    RESULTS / "station_highway_connectivity.csv"
)


# ============================================================
# SETTINGS
# ============================================================

RADIUS_500_M = 500
RADIUS_1_KM = 1000
RADIUS_5_KM = 5000


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("STATION CANDIDATE - HIGHWAY CONNECTIVITY ANALYSIS")
print("=" * 80)

stations = gpd.read_file(
    STATION_FILE,
    layer="station_candidates"
)

highways = gpd.read_file(
    HIGHWAY_FILE
)

print(f"Station candidates: {len(stations)}")
print(f"Highway features: {len(highways)}")


# ============================================================
# PROJECT TO METRIC CRS
# ============================================================

stations_metric = stations.to_crs(
    "EPSG:32643"
)

highways_metric = highways.to_crs(
    "EPSG:32643"
)


# ============================================================
# SPATIAL INDEX
# ============================================================

highway_sindex = highways_metric.sindex


# ============================================================
# ANALYZE EACH STATION CANDIDATE
# ============================================================

results = []

for _, station in stations_metric.iterrows():

    candidate_id = station["candidate_id"]
    route = station["route"]
    chainage = station["chainage_km"]

    point = station.geometry

    # Search area
    search_area = point.buffer(
        RADIUS_5_KM
    )

    possible_indices = list(
        highway_sindex.intersection(
            search_area.bounds
        )
    )

    if not possible_indices:

        results.append({
            "candidate_id": candidate_id,
            "route": route,
            "chainage_km": chainage,
            "highways_within_500m": 0,
            "highways_within_1km": 0,
            "highways_within_5km": 0,
            "nearest_highway_distance_m": None,
            "nearest_highway_distance_km": None,
            "nearest_highway": None,
            "nearest_highway_type": None,
            "nearest_highway_state": None
        })

        continue

    nearby = highways_metric.iloc[
        possible_indices
    ].copy()

    # Exact distance from station candidate
    nearby["distance_m"] = (
        nearby.geometry.distance(point)
    )

    # Keep highways within 5 km
    nearby = nearby[
        nearby["distance_m"] <= RADIUS_5_KM
    ].copy()

    if nearby.empty:

        results.append({
            "candidate_id": candidate_id,
            "route": route,
            "chainage_km": chainage,
            "highways_within_500m": 0,
            "highways_within_1km": 0,
            "highways_within_5km": 0,
            "nearest_highway_distance_m": None,
            "nearest_highway_distance_km": None,
            "nearest_highway": None,
            "nearest_highway_type": None,
            "nearest_highway_state": None
        })

        continue

    # Sort nearest first
    nearby = nearby.sort_values(
        "distance_m"
    )

    nearest = nearby.iloc[0]

    # Counts
    count_500m = (
        nearby["distance_m"] <= RADIUS_500_M
    ).sum()

    count_1km = (
        nearby["distance_m"] <= RADIUS_1_KM
    ).sum()

    count_5km = (
        nearby["distance_m"] <= RADIUS_5_KM
    ).sum()

    results.append({
        "candidate_id": candidate_id,
        "route": route,
        "chainage_km": chainage,

        "highways_within_500m": int(
            count_500m
        ),

        "highways_within_1km": int(
            count_1km
        ),

        "highways_within_5km": int(
            count_5km
        ),

        "nearest_highway_distance_m": round(
            float(nearest["distance_m"]),
            2
        ),

        "nearest_highway_distance_km": round(
            float(nearest["distance_m"]) / 1000,
            4
        ),

        "nearest_highway": nearest[
            "road_name"
        ],

        "nearest_highway_type": nearest[
            "road_type"
        ],

        "nearest_highway_state": nearest[
            "state_ut"
        ]
    })


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

result = pd.DataFrame(
    results
)


# ============================================================
# ACCESS FLAGS
# ============================================================

result["highway_within_500m"] = (
    result["highways_within_500m"] > 0
)

result["highway_within_1km"] = (
    result["highways_within_1km"] > 0
)

result["highway_within_5km"] = (
    result["highways_within_5km"] > 0
)


# ============================================================
# SAVE CSV
# ============================================================

RESULTS.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    CSV_FILE,
    index=False
)


# ============================================================
# CREATE GIS OUTPUT
# ============================================================

result_gdf = stations[
    [
        "candidate_id",
        "geometry"
    ]
].merge(
    result,
    on="candidate_id",
    how="left"
)

result_gdf = gpd.GeoDataFrame(
    result_gdf,
    geometry="geometry",
    crs=stations.crs
)


if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


result_gdf.to_file(
    OUTPUT_FILE,
    layer="station_highway_connectivity",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("CORRECTED HIGHWAY CONNECTIVITY SUMMARY")
print("=" * 80)

summary = (
    result
    .groupby("route")
    .agg(
        candidates=("candidate_id", "count"),
        highway_within_500m=(
            "highway_within_500m",
            "sum"
        ),
        highway_within_1km=(
            "highway_within_1km",
            "sum"
        ),
        highway_within_5km=(
            "highway_within_5km",
            "sum"
        ),
        average_nearest_highway_km=(
            "nearest_highway_distance_km",
            "mean"
        ),
        minimum_nearest_highway_km=(
            "nearest_highway_distance_km",
            "min"
        ),
        maximum_nearest_highway_km=(
            "nearest_highway_distance_km",
            "max"
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
# OUTPUT
# ============================================================

print()
print("CSV:")
print(CSV_FILE)

print()
print("GeoPackage:")
print(OUTPUT_FILE)

print()
print(
    "Corrected highway connectivity analysis completed."
)