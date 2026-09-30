import geopandas as gpd
import requests
from shapely.geometry import shape

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

    data = response.json()

    return data.get("features", [])


# ---------------------------------------------------------
# 1. Read Route 1 centerline
# ---------------------------------------------------------

route = gpd.read_file(ROUTE)

print("Route CRS:", route.crs)

centerline = route.to_crs(32643).geometry.iloc[0]

print(
    "Centerline length:",
    round(centerline.length / 1000, 3),
    "km"
)


# ---------------------------------------------------------
# 2. Create 3.5 m permanent footprint
# ---------------------------------------------------------

footprint = centerline.buffer(1.75)

print(
    "3.5 m footprint area:",
    round(footprint.area, 2),
    "m²"
)


# ---------------------------------------------------------
# 3. Select one test point around 394 km
# ---------------------------------------------------------

distance = 394_000

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

print(
    "\nTest point:",
    "lon =", round(lon, 6),
    "lat =", round(lat, 6)
)


# ---------------------------------------------------------
# 4. Query Bhuvan
# ---------------------------------------------------------

features = query_lulc(lon, lat)

print(
    "WMS features returned:",
    len(features)
)


if not features:

    print("No LULC feature returned.")

    raise SystemExit


# ---------------------------------------------------------
# 5. Convert first WMS feature to geometry
# ---------------------------------------------------------

feature = features[0]

lulc_geometry = shape(
    feature["geometry"]
)

properties = feature["properties"]

print(
    "LULC:",
    properties.get("Level_I")
)

print(
    "Level II:",
    properties.get("Level_II")
)

print(
    "Level IV:",
    properties.get("Level_lV")
)


# ---------------------------------------------------------
# 6. Convert LULC polygon to projected CRS
# ---------------------------------------------------------

lulc = gpd.GeoDataFrame(
    [properties],
    geometry=[lulc_geometry],
    crs="EPSG:4326"
)

lulc = lulc.to_crs(32643)


# ---------------------------------------------------------
# 7. Intersect with 3.5 m footprint
# ---------------------------------------------------------

intersection = lulc.geometry.iloc[0].intersection(
    footprint
)


# ---------------------------------------------------------
# 8. Calculate actual impacted area
# ---------------------------------------------------------

impact_area_m2 = intersection.area

impact_area_km2 = impact_area_m2 / 1_000_000


print(
    "\nACTUAL 3.5 m FOOTPRINT IMPACT"
)

print(
    "LULC class:",
    properties.get("Level_I")
)

print(
    "Impact area:",
    round(impact_area_m2, 4),
    "m²"
)

print(
    "Impact area:",
    round(impact_area_km2, 8),
    "km²"
)