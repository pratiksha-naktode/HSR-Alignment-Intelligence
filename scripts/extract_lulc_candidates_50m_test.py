import geopandas as gpd
import requests
import hashlib
from shapely.geometry import shape

# =========================================================
# CONFIGURATION
# =========================================================

ROUTE = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R1\R1\ROUTE 1.shp"

OUTPUT = r"data\processed\Route_1_lulc_candidates_test.gpkg"

WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/ows"

LAYER = "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_MH"

SAMPLE_INTERVAL_M = 50

TEST_LENGTH_M = 10_000

# HSR permanent ground footprint
FOOTPRINT_HALF_WIDTH_M = 1.75


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

        # CRS:84 avoids WMS 1.3 latitude/longitude axis-order issue
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

    response = requests.get(
        WMS_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json().get("features", [])


# =========================================================
# 1. LOAD ROUTE
# =========================================================

print("Loading Route 1...")

route = gpd.read_file(ROUTE)

print("Original CRS:", route.crs)

route = route.to_crs(32643)

centerline = route.geometry.iloc[0]

print(
    "Route length:",
    round(centerline.length / 1000, 3),
    "km"
)


# =========================================================
# 2. CREATE 3.5 m PERMANENT FOOTPRINT
# =========================================================

footprint = centerline.buffer(
    FOOTPRINT_HALF_WIDTH_M
)

test_footprint = centerline.interpolate(
    0
)

print(
    "3.5 m footprint width:",
    FOOTPRINT_HALF_WIDTH_M * 2,
    "m"
)


# =========================================================
# 3. SAMPLE FIRST 10 KM
# =========================================================

test_length = min(
    TEST_LENGTH_M,
    centerline.length
)

distances = list(
    range(
        0,
        int(test_length) + 1,
        SAMPLE_INTERVAL_M
    )
)

print(
    "Test length:",
    test_length / 1000,
    "km"
)

print(
    "Samples:",
    len(distances)
)


# =========================================================
# 4. DISCOVER LULC POLYGONS
# =========================================================

unique_polygons = {}

successful_samples = 0

failed_samples = 0


for index, distance in enumerate(distances):

    point_utm = centerline.interpolate(distance)

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

        if features:
            successful_samples += 1

        print(
            f"[{index + 1}/{len(distances)}] "
            f"{distance / 1000:.2f} km -> "
            f"{len(features)} feature(s)"
        )

        for feature in features:

            geometry_data = feature.get(
                "geometry"
            )

            if not geometry_data:
                continue

            geometry = shape(
                geometry_data
            )

            # -------------------------------------------------
            # Geometry-based unique identifier
            # -------------------------------------------------

            geometry_hash = hashlib.md5(
                geometry.wkb
            ).hexdigest()

            properties = feature.get(
                "properties",
                {}
            )

            # -------------------------------------------------
            # Store only first occurrence
            # -------------------------------------------------

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

                    "source_lon":
                        lon,

                    "source_lat":
                        lat,

                    "geometry_hash":
                        geometry_hash,
                }

    except Exception as e:

        failed_samples += 1

        print(
            "   ERROR:",
            e
        )


# =========================================================
# 5. CREATE GEODATAFRAME
# =========================================================

print("\n----------------------------------------")

print(
    "Successful samples:",
    successful_samples
)

print(
    "Failed samples:",
    failed_samples
)

print(
    "Unique polygons:",
    len(unique_polygons)
)


records = list(
    unique_polygons.values()
)


if not records:

    print(
        "\nNo LULC polygons discovered."
    )

    raise SystemExit


lulc = gpd.GeoDataFrame(
    records,
    geometry="geometry",
    crs="EPSG:4326"
)


# =========================================================
# 6. REPROJECT TO METRIC CRS
# =========================================================

lulc = lulc.to_crs(32643)


# =========================================================
# 7. CALCULATE INTERSECTION WITH 3.5 m FOOTPRINT
# =========================================================

print(
    "\nCalculating actual 3.5 m footprint intersections..."
)


impact_areas = []

intersection_geometries = []


for _, row in lulc.iterrows():

    intersection = row.geometry.intersection(
        footprint
    )

    area_m2 = intersection.area

    impact_areas.append(
        area_m2
    )

    intersection_geometries.append(
        intersection
    )


lulc["impact_area_m2"] = impact_areas

lulc["impact_area_km2"] = (
    lulc["impact_area_m2"]
    / 1_000_000
)


# =========================================================
# 8. REMOVE POLYGONS WITH ZERO IMPACT
# =========================================================

lulc = lulc[
    lulc["impact_area_m2"] > 0
].copy()


print(
    "Polygons actually intersecting footprint:",
    len(lulc)
)


# =========================================================
# 9. PRINT CLASS SUMMARY
# =========================================================

print("\nLULC IMPACT SUMMARY")
print("----------------------------------------")


summary = (
    lulc
    .groupby("Level_I")["impact_area_km2"]
    .sum()
    .sort_values(
        ascending=False
    )
)


for land_class, area in summary.items():

    print(
        f"{land_class}: "
        f"{area:.8f} km²"
    )


# =========================================================
# 10. SAVE RESULTS
# =========================================================

lulc.to_file(
    OUTPUT,
    layer="lulc_candidates",
    driver="GPKG"
)


print("\n----------------------------------------")

print(
    "Saved:",
    OUTPUT
)

print(
    "Total impacted area:",
    round(
        lulc["impact_area_km2"].sum(),
        8
    ),
    "km²"
)

print("----------------------------------------")