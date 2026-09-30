import geopandas as gpd
import requests
import hashlib
import time
import os
from shapely.geometry import shape

# =========================================================
# CONFIG
# =========================================================

ROUTE = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R1\R1\ROUTE 1.shp"

WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/ows"

LAYER = "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_MH"

PROCESSED_DIR = r"data\processed"
RESULTS_DIR = r"data\results"

OUTPUT_GPKG = os.path.join(
    PROCESSED_DIR,
    "Route_1_lulc_intersections_final.gpkg"
)

OUTPUT_CSV = os.path.join(
    RESULTS_DIR,
    "Route_1_lulc_summary.csv"
)

FOREST_DETAILS_CSV = os.path.join(
    RESULTS_DIR,
    "Route_1_forest_patch_details.csv"
)

FOREST_DETAILS_GPKG = os.path.join(
    PROCESSED_DIR,
    "Route_1_forest_patch_details.gpkg"
)

SAMPLE_INTERVAL_M = 100

FOOTPRINT_HALF_WIDTH_M = 1.75

MAX_RETRIES = 3

RETRY_DELAY = 2


# =========================================================
# WMS QUERY
# =========================================================

def query_lulc(lon, lat):

    delta = 0.001

    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetFeatureInfo",

        "layers": LAYER,
        "query_layers": LAYER,

        "info_format": "application/json",

        "crs": "CRS:84",

        "bbox": (
            f"{lon-delta},"
            f"{lat-delta},"
            f"{lon+delta},"
            f"{lat+delta}"
        ),

        "width": "1000",
        "height": "1000",

        "i": "500",
        "j": "500",

        "feature_count": "10",
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                WMS_URL,
                params=params,
                timeout=60
            )

            response.raise_for_status()

            return response.json().get(
                "features",
                []
            )

        except Exception as e:

            print(
                f"   Retry {attempt}/{MAX_RETRIES}: {e}"
            )

            if attempt < MAX_RETRIES:

                time.sleep(RETRY_DELAY)

            else:

                raise


# =========================================================
# LOAD ROUTE
# =========================================================

print("\nLoading Route 1...")

route = gpd.read_file(ROUTE)

print(
    "Original CRS:",
    route.crs
)

route = route.to_crs(32643)

centerline = route.geometry.iloc[0]

print(
    "Route length:",
    round(centerline.length / 1000, 3),
    "km"
)


# =========================================================
# 3.5 m FOOTPRINT
# =========================================================

footprint = centerline.buffer(
    FOOTPRINT_HALF_WIDTH_M
)

print(
    "Permanent footprint:",
    FOOTPRINT_HALF_WIDTH_M * 2,
    "m"
)

print(
    "Footprint area:",
    round(footprint.area, 2),
    "m²"
)


# =========================================================
# SAMPLE POINTS
# =========================================================

distances = list(
    range(
        0,
        int(centerline.length) + 1,
        SAMPLE_INTERVAL_M
    )
)

# Make sure exact endpoint is included

if distances[-1] != centerline.length:

    distances.append(
        centerline.length
    )


print(
    "Sampling interval:",
    SAMPLE_INTERVAL_M,
    "m"
)

print(
    "Total samples:",
    len(distances)
)


# =========================================================
# DISCOVER UNIQUE POLYGONS
# =========================================================

unique_polygons = {}

successful_samples = 0

failed_samples = 0


for index, distance in enumerate(distances):

    point_utm = centerline.interpolate(
        distance
    )

    point_wgs84 = (
        gpd.GeoSeries(
            [point_utm],
            crs=32643
        )
        .to_crs(4326)
        .iloc[0]
    )

    lon = point_wgs84.x
    lat = point_wgs84.y

    try:

        features = query_lulc(
            lon,
            lat
        )

        successful_samples += 1

        for feature in features:

            geometry_data = feature.get(
                "geometry"
            )

            if not geometry_data:
                continue

            geometry = shape(
                geometry_data
            )

            # Geometry itself identifies polygon
            geometry_hash = hashlib.md5(
                geometry.wkb
            ).hexdigest()

            properties = feature.get(
                "properties",
                {}
            )

            if geometry_hash not in unique_polygons:

                unique_polygons[
                    geometry_hash
                ] = {

                    "geometry": geometry,

                    "REG_DESCRI":
                        properties.get(
                            "REG_DESCRI"
                        ),

                    "LULC_1":
                        properties.get(
                            "LULC_1"
                        ),

                    "LULC_2":
                        properties.get(
                            "LULC_2"
                        ),

                    "LULC_3":
                        properties.get(
                            "LULC_3"
                        ),

                    "Level_I":
                        properties.get(
                            "Level_I"
                        ),

                    "Level_II":
                        properties.get(
                            "Level_II"
                        ),

                    "Level_lV":
                        properties.get(
                            "Level_lV"
                        ),

                    "first_sample_km":
                        distance / 1000,

                    "geometry_hash":
                        geometry_hash
                }

    except Exception as e:

        failed_samples += 1

        print(
            f"\nFAILED at "
            f"{distance/1000:.2f} km: {e}"
        )

    # Progress every 100 samples

    if (
        (index + 1) % 100 == 0
        or index == len(distances) - 1
    ):

        print(
            f"\nProgress: "
            f"{index + 1}/{len(distances)} "
            f"| Unique polygons: "
            f"{len(unique_polygons)} "
            f"| Failed: "
            f"{failed_samples}"
        )


# =========================================================
# CREATE LULC GEODATAFRAME
# =========================================================

print("\n========================================")

print(
    "Successful samples:",
    successful_samples
)

print(
    "Failed samples:",
    failed_samples
)

print(
    "Unique polygons discovered:",
    len(unique_polygons)
)

print("========================================")


records = list(
    unique_polygons.values()
)


if not records:

    raise RuntimeError(
        "No LULC polygons were discovered."
    )


lulc = gpd.GeoDataFrame(
    records,
    geometry="geometry",
    crs="EPSG:4326"
)


# =========================================================
# PROJECT TO METRIC CRS
# =========================================================

lulc = lulc.to_crs(32643)


# =========================================================
# ACTUAL 3.5 m INTERSECTION
# =========================================================

print(
    "\nCalculating 3.5 m footprint intersections..."
)


impact_areas = []


for _, row in lulc.iterrows():

    intersection = (
        row.geometry
        .intersection(footprint)
    )

    area_m2 = intersection.area

    impact_areas.append(
        area_m2
    )


lulc[
    "impact_area_m2"
] = impact_areas


lulc[
    "impact_area_km2"
] = (
    lulc["impact_area_m2"]
    / 1_000_000
)


# =========================================================
# KEEP ONLY ACTUAL INTERSECTIONS
# =========================================================

lulc = lulc[
    lulc["impact_area_m2"] > 0
].copy()


# =========================================================
# DETAILED FOREST PATCH CALCULATION
# =========================================================

print("\nCreating detailed Forest patch calculation...")

forest_lulc = lulc[
    lulc["Level_I"].fillna("").astype(str).str.strip().str.lower() == "forest"
].copy()

if not forest_lulc.empty:
    forest_wgs84 = forest_lulc.to_crs(4326)

    forest_lulc["forest_patch_id"] = range(1, len(forest_lulc) + 1)
    forest_lulc["chainage_km"] = forest_lulc["first_sample_km"]

    forest_lulc["latitude"] = forest_wgs84.geometry.centroid.y.values
    forest_lulc["longitude"] = forest_wgs84.geometry.centroid.x.values

    forest_lulc["calculation"] = (
        forest_lulc["impact_area_m2"].map(
            lambda x: f"{x:.6f} / 1,000,000"
        )
    )

    forest_details = forest_lulc[
        [
            "forest_patch_id",
            "chainage_km",
            "latitude",
            "longitude",
            "impact_area_m2",
            "calculation",
            "impact_area_km2",
            "geometry"
        ]
    ].copy()

    forest_details = forest_details.rename(
        columns={
            "impact_area_m2": "affected_area_m2",
            "impact_area_km2": "affected_area_km2"
        }
    )

    # CSV contains the audit/calculation table without geometry.
    forest_details.drop(columns="geometry").to_csv(
        FOREST_DETAILS_CSV,
        index=False
    )

    # GPKG preserves the actual intersected Forest patch geometry.
    forest_details.to_file(
        FOREST_DETAILS_GPKG,
        layer="forest_patch_details",
        driver="GPKG"
    )

    forest_total_km2 = forest_details["affected_area_km2"].sum()

    print(
        f"Forest patches: {len(forest_details)}"
    )
    print(
        f"Forest affected area: {forest_total_km2:.8f} km²"
    )
    print(
        f"Forest details CSV: {FOREST_DETAILS_CSV}"
    )
    print(
        f"Forest details GPKG: {FOREST_DETAILS_GPKG}"
    )
else:
    forest_details = gpd.GeoDataFrame(
        columns=[
            "forest_patch_id",
            "chainage_km",
            "latitude",
            "longitude",
            "affected_area_m2",
            "calculation",
            "affected_area_km2",
            "geometry"
        ],
        geometry="geometry",
        crs="EPSG:32643"
    )

    forest_details.drop(columns="geometry").to_csv(
        FOREST_DETAILS_CSV,
        index=False
    )

    forest_total_km2 = 0.0

    print("No Forest patches intersect the 3.5 m footprint.")


# =========================================================
# CLASS SUMMARY
# =========================================================

summary = (
    lulc
    .groupby("Level_I")[
        "impact_area_km2"
    ]
    .sum()
    .reset_index()
)


summary.columns = [
    "land_class",
    "impact_area_km2"
]


# =========================================================
# VERIFY FOREST TOTAL
# =========================================================

forest_summary_value = summary.loc[
    summary["land_class"].fillna("").astype(str).str.strip().str.lower() == "forest",
    "impact_area_km2"
].sum()

forest_difference = forest_summary_value - forest_total_km2

print(
    "\nFOREST CALCULATION VERIFICATION"
)
print(
    f"Detailed Forest patches total: {forest_total_km2:.8f} km²"
)
print(
    f"Summary Forest total:          {forest_summary_value:.8f} km²"
)
print(
    f"Difference:                    {forest_difference:.12f} km²"
)

if abs(forest_difference) > 1e-12:
    raise RuntimeError(
        "Forest detailed total does not match the Forest summary total."
    )
else:
    print("Verification: PASSED")


# =========================================================
# ADD REQUIRED CLASSES
# =========================================================

required_classes = [
    "Forest",
    "Agriculture",
    "Built-up"
]


for land_class in required_classes:

    if land_class not in set(
        summary["land_class"]
    ):

        summary.loc[
            len(summary)
        ] = [
            land_class,
            0.0
        ]


summary = summary.sort_values(
    "land_class"
).reset_index(drop=True)


# =========================================================
# SAVE SUMMARY
# =========================================================

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)

summary.to_csv(
    OUTPUT_CSV,
    index=False
)


# =========================================================
# SAVE GEOPACKAGE
# =========================================================

os.makedirs(
    PROCESSED_DIR,
    exist_ok=True
)

lulc.to_file(
    OUTPUT_GPKG,
    layer="lulc_intersections",
    driver="GPKG"
)


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n========================================")
print("ROUTE 1 LULC FINAL SUMMARY")
print("========================================")

for _, row in summary.iterrows():

    print(
        f"{row['land_class']}: "
        f"{row['impact_area_km2']:.8f} km²"
    )


print(
    "\nTotal impacted LULC area:",
    round(
        summary[
            "impact_area_km2"
        ].sum(),
        8
    ),
    "km²"
)

print(
    "\nLULC polygons intersecting footprint:",
    len(lulc)
)

print(
    "Results CSV:",
    OUTPUT_CSV
)

print(
    "Results GPKG:",
    OUTPUT_GPKG
)

print("========================================")