import os
import time
import hashlib
import warnings

import requests
import geopandas as gpd
import pandas as pd

from shapely.geometry import shape, Point
from shapely import wkb
from shapely.ops import transform
from pyproj import Transformer

warnings.filterwarnings("ignore")


# ============================================================
# HSR ROUTE OPTIMIZATION PROJECT
# ROUTE 2 - LULC IMPACT ANALYSIS
# ============================================================
#
# Methodology:
#
# 1. Load Route 2 centerline
# 2. Reproject to UTM 43N
# 3. Create 3.5 m permanent ground footprint
#    - 1.75 m on each side of centerline
# 4. Sample centerline every 100 m
# 5. Query Bhuvan WMS LULC
# 6. Cache discovered polygons
# 7. Avoid repeated WMS requests when a sample point
#    is already inside a previously discovered polygon
# 8. Deduplicate polygons using geometry hash
# 9. Intersect all discovered polygons with 3.5 m footprint
# 10. Calculate impact area in km²
#
# IMPORTANT:
# Gauge = 1.435 m is NOT used for footprint calculation.
# ROW / planning width = 17.5 m is NOT used here.
# Permanent ground footprint = 3.5 m.
# ============================================================


# ============================================================
# PROJECT PATH
# ============================================================

BASE = r"C:\Users\Texaxs\Desktop\hsr-route-optimization"


# ============================================================
# ROUTE 2 SOURCE
# ============================================================

ROUTE_FILE = (
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT"
    r"\RouteData\R3\R3\ROUTE 3.shp"
)


# ============================================================
# OUTPUTS
# ============================================================

PROCESSED_DIR = os.path.join(
    BASE,
    "data",
    "processed"
)

RESULTS_DIR = os.path.join(
    BASE,
    "data",
    "results"
)

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


OUTPUT_GPKG = os.path.join(
    PROCESSED_DIR,
    "Route_3_lulc_intersections_final.gpkg"
)

OUTPUT_CSV = os.path.join(
    RESULTS_DIR,
"Route_3_lulc_summary.csv")


# ============================================================
# CRS
# ============================================================

SOURCE_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:32643"

to_metric = Transformer.from_crs(
    SOURCE_CRS,
    METRIC_CRS,
    always_xy=True
).transform


# ============================================================
# HSR FOOTPRINT
# ============================================================

GROUND_FOOTPRINT_M = 3.5
HALF_FOOTPRINT_M = 1.75

SAMPLING_INTERVAL_M = 100


# ============================================================
# BHUVAN WMS
# ============================================================

WMS_URL = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms"
)


# Verified statewide LULC layers
LULC_LAYERS = [
    (
        "Maharashtra",
        "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_MH"
    ),
    (
        "Karnataka",
        "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_KA"
    ),
    (
        "Telangana",
        "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_TS"
    ),
]


# ============================================================
# WMS SETTINGS
# ============================================================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3

RETRY_DELAY = 1.5

BBOX_HALF_SIZE = 0.001


# ============================================================
# CATEGORY MAPPING
# ============================================================

def classify_lulc(properties):
    """
    Convert Bhuvan Level_I hierarchy into
    project-level LULC categories.
    """

    level_i = str(
        properties.get("Level_I", "")
    ).strip()

    if level_i == "Agriculture":
        return "Agriculture"

    if level_i == "Built-up":
        return "Built-up"

    if level_i == "Forest":
        return "Forest"

    if level_i == "Wastelands":
        return "Wastelands"

    if level_i == "Water Bodies":
        return "Water Bodies"

    if level_i == "Wetlands":
        return "Wetlands"

    return "Others"


# ============================================================
# GEOMETRY HASH
# ============================================================

def geometry_hash(geom):
    """
    Create stable hash for polygon deduplication.
    """

    try:
        return hashlib.sha256(
            geom.wkb
        ).hexdigest()
    except Exception:
        return None


# ============================================================
# WMS FEATURE INFO
# ============================================================

def query_wms(
    lon,
    lat,
    layer_name,
    session
):
    """
    Query one LULC location using WMS GetFeatureInfo.

    CRS:84 is deliberately used because this is the
    axis-order configuration already verified for Bhuvan.
    """

    bbox = (
        lon - BBOX_HALF_SIZE,
        lat - BBOX_HALF_SIZE,
        lon + BBOX_HALF_SIZE,
        lat + BBOX_HALF_SIZE,
    )

    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetFeatureInfo",

        "layers": layer_name,
        "query_layers": layer_name,

        "info_format": "application/json",

        "crs": "CRS:84",

        "bbox": ",".join(
            str(v) for v in bbox
        ),

        "width": 1000,
        "height": 1000,

        "i": 500,
        "j": 500,

        "feature_count": 10,
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.get(
                WMS_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
                verify=False
            )

            response.raise_for_status()

            data = response.json()

            features = data.get(
                "features",
                []
            )

            return features

        except Exception as e:

            print(
                f"   Retry {attempt}/{MAX_RETRIES}: {e}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return []


# ============================================================
# LOAD ROUTE
# ============================================================

print("=" * 70)
print("ROUTE 2 - LULC IMPACT ANALYSIS")
print("=" * 70)

print("\nLoading Route 2...")

if not os.path.exists(ROUTE_FILE):

    raise FileNotFoundError(
        f"Route 2 file not found:\n{ROUTE_FILE}"
    )

route = gpd.read_file(
    ROUTE_FILE
)

if route.empty:

    raise ValueError(
        "Route 2 contains no geometry."
    )


print(
    f"Original CRS: {route.crs}"
)


# ============================================================
# NORMALIZE CRS
# ============================================================

route = route.to_crs(
    SOURCE_CRS
)


# ============================================================
# COMBINE ROUTE GEOMETRIES
# ============================================================

route_line = route.geometry.union_all()


if route_line.geom_type == "MultiLineString":

    # Merge if possible
    from shapely.ops import linemerge

    route_line = linemerge(
        route_line
    )


# ============================================================
# CREATE METRIC CENTERLINE
# ============================================================

route_metric = transform(
    to_metric,
    route_line
)


route_length_m = route_metric.length

route_length_km = (
    route_length_m / 1000.0
)


print(
    f"Route length: {route_length_km:.3f} km"
)


# ============================================================
# CREATE 3.5m FOOTPRINT
# ============================================================

footprint = route_metric.buffer(
    HALF_FOOTPRINT_M,
    cap_style=2,
    join_style=2
)


footprint_area_m2 = footprint.area


print(
    f"Permanent footprint: "
    f"{GROUND_FOOTPRINT_M} m"
)

print(
    f"Footprint area: "
    f"{footprint_area_m2:.2f} m²"
)


# ============================================================
# CREATE 100m SAMPLE POINTS
# ============================================================

print(
    f"Sampling interval: "
    f"{SAMPLING_INTERVAL_M} m"
)


sample_distances = list(
    range(
        0,
        int(route_length_m),
        SAMPLING_INTERVAL_M
    )
)


# Always include final point
if not sample_distances or (
    sample_distances[-1] < route_length_m
):

    sample_distances.append(
        route_length_m
    )


print(
    f"Total samples: "
    f"{len(sample_distances)}"
)


# ============================================================
# TRANSFORMER
# ============================================================

to_wgs84 = Transformer.from_crs(
    METRIC_CRS,
    SOURCE_CRS,
    always_xy=True
).transform


# ============================================================
# SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent":
        "HSR-Route-Optimization-LULC/1.0"
})


# ============================================================
# POLYGON CACHE
# ============================================================
#
# The major optimization:
#
# If a 100m sample point is already inside a polygon
# previously returned by WMS, we don't query WMS again.
#
# This keeps the 100m sampling positions but reduces
# unnecessary requests.
# ============================================================

polygon_cache = []

polygon_hashes = set()

failed_samples = []

successful_samples = 0

skipped_cached = 0


# ============================================================
# WMS SAMPLING
# ============================================================

for index, distance_m in enumerate(
    sample_distances,
    start=1
):

    # --------------------------------------------------------
    # Point on centerline
    # --------------------------------------------------------

    point_metric = route_metric.interpolate(
        distance_m
    )

    point_wgs84 = transform(
        to_wgs84,
        point_metric
    )

    lon = point_wgs84.x
    lat = point_wgs84.y


    # --------------------------------------------------------
    # Check existing cached polygons
    # --------------------------------------------------------

    sample_point = Point(
        lon,
        lat
    )

    already_known = False

    for cached in polygon_cache:

        cached_geom = cached["geometry"]

        try:

            if cached_geom.covers(
                sample_point
            ):

                already_known = True
                skipped_cached += 1

                break

        except Exception:
            continue


    # --------------------------------------------------------
    # If already known, skip WMS
    # --------------------------------------------------------

    if already_known:

        if (
            index % 100 == 0
            or index == len(sample_distances)
        ):

            print(
                f"Progress: "
                f"{index}/{len(sample_distances)} "
                f"| Unique polygons: "
                f"{len(polygon_cache)} "
                f"| Cached skips: "
                f"{skipped_cached} "
                f"| Failed: "
                f"{len(failed_samples)}"
            )

        continue


    # --------------------------------------------------------
    # Query WMS layers
    # --------------------------------------------------------

    features = []

    for state_name, layer_name in LULC_LAYERS:

        features = query_wms(
            lon,
            lat,
            layer_name,
            session
        )

        if features:

            break


    # --------------------------------------------------------
    # No feature
    # --------------------------------------------------------

    if not features:

        failed_samples.append({
            "distance_m": distance_m,
            "longitude": lon,
            "latitude": lat,
        })

        if (
            index % 100 == 0
            or index == len(sample_distances)
        ):

            print(
                f"Progress: "
                f"{index}/{len(sample_distances)} "
                f"| Unique polygons: "
                f"{len(polygon_cache)} "
                f"| Cached skips: "
                f"{skipped_cached} "
                f"| Failed: "
                f"{len(failed_samples)}"
            )

        continue


    successful_samples += 1


    # --------------------------------------------------------
    # Process returned features
    # --------------------------------------------------------

    for feature in features:

        geometry_json = feature.get(
            "geometry"
        )

        properties = feature.get(
            "properties",
            {}
        )


        if not geometry_json:
            continue


        try:

            geom = shape(
                geometry_json
            )

        except Exception:

            continue


        if geom.is_empty:
            continue


        if not geom.is_valid:

            try:
                geom = geom.buffer(0)
            except Exception:
                continue


        if geom.is_empty:
            continue


        # ----------------------------------------------------
        # Only polygon geometries
        # ----------------------------------------------------

        if geom.geom_type not in (
            "Polygon",
            "MultiPolygon"
        ):
            continue


        # ----------------------------------------------------
        # Deduplicate
        # ----------------------------------------------------

        geom_hash = geometry_hash(
            geom
        )

        if geom_hash is None:
            continue


        if geom_hash in polygon_hashes:
            continue


        polygon_hashes.add(
            geom_hash
        )


        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        category = classify_lulc(
            properties
        )


        # ----------------------------------------------------
        # Store polygon
        # ----------------------------------------------------

        polygon_cache.append({
            "geometry": geom,
            "category": category,

            "level_i": properties.get(
                "Level_I"
            ),

            "level_ii": properties.get(
                "Level_II"
            ),

            "level_iii": properties.get(
                "Level_III"
            ),

            "level_iv": properties.get(
                "Level_IV"
            ),

            "lulc_1": properties.get(
                "LULC_1"
            ),

            "lulc_2": properties.get(
                "LULC_2"
            ),

            "lulc_3": properties.get(
                "LULC_3"
            ),

            "reg_descri": properties.get(
                "REG_DESCRI"
            ),

            "area_sqkm_wms": properties.get(
                "Area_SqKm"
            ),

            "sample_distance_m": distance_m,

            "sample_longitude": lon,

            "sample_latitude": lat,

            "geometry_hash": geom_hash,
        })


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if (
        index % 100 == 0
        or index == len(sample_distances)
    ):

        print(
            f"Progress: "
            f"{index}/{len(sample_distances)} "
            f"| Unique polygons: "
            f"{len(polygon_cache)} "
            f"| Cached skips: "
            f"{skipped_cached} "
            f"| Failed: "
            f"{len(failed_samples)}"
        )


# ============================================================
# WMS COMPLETE
# ============================================================

print("\n" + "=" * 70)

print(
    "WMS SAMPLING COMPLETE"
)

print("=" * 70)

print(
    f"Successful WMS samples: "
    f"{successful_samples}"
)

print(
    f"Cached sample skips: "
    f"{skipped_cached}"
)

print(
    f"Failed samples: "
    f"{len(failed_samples)}"
)

print(
    f"Unique polygons discovered: "
    f"{len(polygon_cache)}"
)


# ============================================================
# CHECK POLYGONS
# ============================================================

if not polygon_cache:

    raise RuntimeError(
        "No LULC polygons were discovered."
    )


# ============================================================
# CREATE GEODATAFRAME
# ============================================================

lulc_wgs84 = gpd.GeoDataFrame(
    polygon_cache,
    geometry="geometry",
    crs=SOURCE_CRS
)


# ============================================================
# REPROJECT TO METRIC CRS
# ============================================================

lulc_metric = lulc_wgs84.to_crs(
    METRIC_CRS
)


# ============================================================
# INTERSECT WITH 3.5m FOOTPRINT
# ============================================================

print(
    "\nCalculating 3.5 m footprint intersections..."
)


# ------------------------------------------------------------
# Spatial intersection
# ------------------------------------------------------------

intersection_mask = (
    lulc_metric.geometry.intersects(
        footprint
    )
)


intersections = lulc_metric.loc[
    intersection_mask
].copy()


print(
    f"LULC polygons intersecting footprint: "
    f"{len(intersections)}"
)


# ============================================================
# CALCULATE ACTUAL IMPACT GEOMETRY
# ============================================================

intersections[
    "impact_geometry"
] = intersections.geometry.intersection(
    footprint
)


intersections[
    "impact_area_m2"
] = intersections[
    "impact_geometry"
].area


intersections[
    "impact_area_km2"
] = (
    intersections[
        "impact_area_m2"
    ] / 1_000_000.0
)


# ============================================================
# REMOVE ZERO-AREA INTERSECTIONS
# ============================================================

intersections = intersections[
    intersections[
        "impact_area_m2"
    ] > 0
].copy()


# ============================================================
# SAVE INTERSECTION GEOMETRY
# ============================================================

# ============================================================
# PREPARE FINAL GPKG GEOMETRY
# ============================================================

# The original LULC polygon geometry is not needed in the
# final GeoPackage. Keep only the actual 3.5 m footprint
# intersection geometry.

intersections = intersections.drop(
    columns=["geometry"],
    errors="ignore"
)

intersections = gpd.GeoDataFrame(
    intersections,
    geometry="impact_geometry",
    crs=METRIC_CRS
)

intersections = intersections.rename_geometry(
    "geometry"
)


# ============================================================
# EXPORT GPKG
# ============================================================

if os.path.exists(
    OUTPUT_GPKG
):

    try:
        os.remove(
            OUTPUT_GPKG
        )
    except PermissionError:

        raise PermissionError(
            f"Close the existing GPKG in QGIS:\n"
            f"{OUTPUT_GPKG}"
        )


intersections.to_file(
    OUTPUT_GPKG,
    layer="route2_lulc",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

summary = (
    intersections
    .groupby("category")[
        "impact_area_km2"
    ]
    .sum()
    .to_dict()
)


categories = [
    "Agriculture",
    "Built-up",
    "Forest",
    "Wastelands",
    "Water Bodies",
    "Wetlands",
    "Others",
]


for category in categories:

    if category not in summary:

        summary[category] = 0.0


# ============================================================
# TOTAL
# ============================================================

total_impact_km2 = sum(
    summary.values()
)


# ============================================================
# CSV
# ============================================================

summary_rows = []

for category in categories:

    summary_rows.append({
        "route": "Route 3",
        "category": category,
        "impact_area_km2": summary[
            category
        ],
    })


summary_rows.append({
    "route": "Route 2",
    "category": "TOTAL",
    "impact_area_km2": total_impact_km2,
})


summary_df = pd.DataFrame(
    summary_rows
)


summary_df.to_csv(
    OUTPUT_CSV,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)

print(
    "ROUTE 2 LULC FINAL SUMMARY"
)

print("=" * 70)

for category in categories:

    print(
        f"{category}: "
        f"{summary[category]:.8f} km²"
    )


print(
    f"\nTotal LULC impact: "
    f"{total_impact_km2:.8f} km²"
)

print(
    f"Total polygons: "
    f"{len(intersections)}"
)

print(
    f"\nCSV: {OUTPUT_CSV}"
)

print(
    f"GPKG: {OUTPUT_GPKG}"
)

print("=" * 70)


# ============================================================
# FAILED SAMPLE LIST
# ============================================================

if failed_samples:

    failed_df = pd.DataFrame(
        failed_samples
    )

    failed_file = os.path.join(
        RESULTS_DIR,
        "Route_2_lulc_failed_samples.csv"
    )

    failed_df.to_csv(
        failed_file,
        index=False
    )

    print(
        f"\nFailed sample list: "
        f"{failed_file}"
    )

else:

    print(
        "\nNo failed samples."
    )


# ============================================================
# CLOSE SESSION
# ============================================================

session.close()

print("\nRoute 2 LULC analysis completed.")