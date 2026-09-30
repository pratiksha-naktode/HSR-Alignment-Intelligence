import geopandas as gpd
import requests
import time

ROUTE = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R1\R1\ROUTE 1.shp"

WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/ows"

LAYER = "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_MH"


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
        "bbox": f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}",
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


# ---------------------------------------------------------
# Load route
# ---------------------------------------------------------

route = gpd.read_file(ROUTE).to_crs(32643)

line = route.geometry.iloc[0]

# First 10 km
test_length = min(10_000, line.length)

distances = range(
    0,
    int(test_length) + 1,
    250
)

print("Route test length:", test_length / 1000, "km")
print("Number of samples:", len(list(distances)))


# ---------------------------------------------------------
# Query WMS
# ---------------------------------------------------------

records = []

for i, distance in enumerate(distances):

    point = line.interpolate(distance)

    point_wgs84 = (
        gpd.GeoSeries(
            [point],
            crs=32643
        )
        .to_crs(4326)
        .iloc[0]
    )

    lon = point_wgs84.x
    lat = point_wgs84.y

    try:

        features = query_lulc(lon, lat)

        for feature in features:

            p = feature.get("properties", {})

            records.append({
                "distance_m": distance,
                "lon": lon,
                "lat": lat,
                "level_i": p.get("Level_I"),
                "level_ii": p.get("Level_II"),
                "level_iv": p.get("Level_lV"),
                "reg_descri": p.get("REG_DESCRI"),
                "geometry": feature.get("geometry")
            })

        print(
            f"{distance/1000:6.2f} km -> "
            f"{len(features)} feature(s)"
        )

    except Exception as e:

        print(
            f"{distance/1000:6.2f} km -> ERROR: {e}"
        )

    time.sleep(0.1)


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\nTotal returned feature records:", len(records))

unique_regions = set(
    r["reg_descri"]
    for r in records
    if r["reg_descri"]
)

print(
    "Unique LULC polygons discovered:",
    len(unique_regions)
)

print("\nLULC classes discovered:")

classes = {}

for r in records:

    key = (
        r["level_i"],
        r["level_ii"]
    )

    classes[key] = classes.get(key, 0) + 1


for key, count in sorted(classes.items()):

    print(
        f"{key[0]} | {key[1]} -> {count} samples"
    )