import geopandas as gpd
import requests
import hashlib
from shapely.geometry import shape

# =========================================================
# CONFIGURATION
# =========================================================

ROUTE = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R1\R1\ROUTE 1.shp"

EXISTING_GPKG = (
    r"data\processed\Route_1_lulc_intersections_final.gpkg"
)

OUTPUT_GPKG = (
    r"data\processed\Route_1_lulc_intersections_corrected.gpkg"
)

OUTPUT_CSV = (
    r"data\results\Route_1_lulc_summary_corrected.csv"
)

WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/ows"

LAYER = (
    "sisdp_phase2:"
    "SISDP_P2_LULC_10K_2016_2019_MH"
)

FOOTPRINT_HALF_WIDTH_M = 1.75

# Previously failed chainages
FAILED_CHAINAGES = [
    93.30,
    93.40,
    93.50,
    93.60,
    93.70,
]


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


# =========================================================
# LOAD ROUTE
# =========================================================

print("Loading Route 1...")

route = gpd.read_file(ROUTE).to_crs(32643)

centerline = route.geometry.iloc[0]

print(
    "Route length:",
    round(centerline.length / 1000, 3),
    "km"
)


# =========================================================
# CREATE 3.5 m FOOTPRINT
# =========================================================

footprint = centerline.buffer(
    FOOTPRINT_HALF_WIDTH_M
)


# =========================================================
# LOAD EXISTING LULC RESULTS
# =========================================================

print("\nLoading existing LULC dataset...")

lulc = gpd.read_file(
    EXISTING_GPKG,
    layer="lulc_intersections"
)

print(
    "Existing polygons:",
    len(lulc)
)


# Existing geometry hashes
existing_hashes = set(
    lulc["geometry_hash"].astype(str)
)


# =========================================================
# RETRIEVE THE FIVE RECOVERED LOCATIONS
# =========================================================

new_records = []


for chainage_km in FAILED_CHAINAGES:

    distance_m = chainage_km * 1000

    point_utm = centerline.interpolate(
        distance_m
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

    print(
        f"\n{chainage_km:.2f} km"
    )

    print(
        "Coordinates:",
        round(lon, 6),
        round(lat, 6)
    )

    features = query_lulc(
        lon,
        lat
    )

    print(
        "Features returned:",
        len(features)
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

        geometry_hash = hashlib.md5(
            geometry.wkb
        ).hexdigest()

        properties = feature.get(
            "properties",
            {}
        )

        print(
            "Class:",
            properties.get("Level_I"),
            "|",
            properties.get("Level_II")
        )

        if geometry_hash in existing_hashes:

            print(
                "Already present."
            )

            continue

        new_records.append({

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
                chainage_km,

            "geometry_hash":
                geometry_hash,
        })


# =========================================================
# ADD NEW POLYGONS
# =========================================================

print(
    "\nNew polygons discovered:",
    len(new_records)
)


if new_records:

    new_lulc = gpd.GeoDataFrame(
        new_records,
        geometry="geometry",
        crs="EPSG:4326"
    )

    new_lulc = new_lulc.to_crs(
        32643
    )

    lulc = gpd.GeoDataFrame(
        lulc,
        geometry="geometry",
        crs=32643
    )

    lulc = gpd.GeoDataFrame(
        __import__("pandas").concat(
            [
                lulc,
                new_lulc
            ],
            ignore_index=True
        ),
        geometry="geometry",
        crs=32643
    )

else:

    print(
        "No new polygons need to be added."
    )


# =========================================================
# RECALCULATE ACTUAL 3.5 m IMPACT
# =========================================================

print(
    "\nRecalculating footprint intersections..."
)


impact_areas = []


for _, row in lulc.iterrows():

    intersection = (
        row.geometry
        .intersection(footprint)
    )

    impact_areas.append(
        intersection.area
    )


lulc[
    "impact_area_m2"
] = impact_areas


lulc[
    "impact_area_km2"
] = (
    lulc[
        "impact_area_m2"
    ] / 1_000_000
)


# Keep actual intersections
lulc = lulc[
    lulc["impact_area_m2"] > 0
].copy()


# =========================================================
# CREATE SUMMARY
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


# Ensure required classes exist
for land_class in [
    "Forest",
    "Agriculture",
    "Built-up"
]:

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
# SAVE
# =========================================================

summary.to_csv(
    OUTPUT_CSV,
    index=False
)

lulc.to_file(
    OUTPUT_GPKG,
    layer="lulc_intersections",
    driver="GPKG"
)


# =========================================================
# FINAL RESULT
# =========================================================

print("\n========================================")
print("ROUTE 1 CORRECTED LULC SUMMARY")
print("========================================")

for _, row in summary.iterrows():

    print(
        f"{row['land_class']}: "
        f"{row['impact_area_km2']:.8f} km²"
    )


print(
    "\nTotal LULC impact:",
    round(
        summary["impact_area_km2"].sum(),
        8
    ),
    "km²"
)

print(
    "Total polygons:",
    len(lulc)
)

print(
    "\nCSV:",
    OUTPUT_CSV
)

print(
    "GPKG:",
    OUTPUT_GPKG
)

print("========================================")