import geopandas as gpd
import numpy as np
import requests
import time

ROUTES = {
    "Route_1": r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R1\R1\ROUTE 1.shp",
    "Route_2": r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R2\R2\ROUTE 2.shp",
    "Route_3": r"C:\Users\Texaxs\Downloads\ROUTE_OPT\RouteData\R3\R3\ROUTE 3.shp",
}

WMS_URL = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/ows"

LAYERS = {
    "Maharashtra": "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_MH",
    "Karnataka": "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_KA",
    "Telangana": "sisdp_phase2:SISDP_P2_LULC_10K_2016_2019_TS",
}


def get_state(lat, lon):
    # Approximate state ranges used only to select the Bhuvan WMS layer.
    if 72.5 <= lon <= 80.0 and 15.5 <= lat <= 22.1:
        # Maharashtra / Karnataka / Telangana overlap requires
        # WMS testing rather than a hard boundary assumption.
        return None
    return None


def query_wms(lon, lat, layer):
    delta = 0.001

    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetFeatureInfo",
        "layers": layer,
        "query_layers": layer,
        "info_format": "application/json",
        "crs": "CRS:84",
        "bbox": f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}",
        "width": "1000",
        "height": "1000",
        "i": "500",
        "j": "500",
        "feature_count": "10",
    }

    response = requests.get(WMS_URL, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        return None

    return features[0]["properties"]


for route_name, path in ROUTES.items():

    print("\n==============================")
    print(route_name)
    print("==============================")

    gdf = gpd.read_file(path)

    line = gdf.to_crs(32643).geometry.iloc[0]
    length = line.length

    distances = np.linspace(0, length, 5)

    for idx, distance in enumerate(distances):

        point_utm = line.interpolate(distance)

        point_wgs84 = (
            gpd.GeoSeries([point_utm], crs=32643)
            .to_crs(4326)
            .iloc[0]
        )

        lon = point_wgs84.x
        lat = point_wgs84.y

        print(
            f"\nPoint {idx + 1}/5"
            f" | chainage = {distance / 1000:.2f} km"
            f" | lon = {lon:.6f}"
            f" | lat = {lat:.6f}"
        )

        found = False

        for state, layer in LAYERS.items():

            try:
                props = query_wms(lon, lat, layer)

                if props:
                    print(f"  State layer: {state}")
                    print(f"  LULC_1: {props.get('LULC_1')}")
                    print(f"  Level_I: {props.get('Level_I')}")
                    print(f"  Level_II: {props.get('Level_II')}")
                    print(f"  Level_IV: {props.get('Level_lV')}")
                    print(f"  Source area: {props.get('Area_SqKm')} km²")

                    found = True
                    break

            except Exception as e:
                print(f"  {state}: query failed - {e}")

        if not found:
            print("  No LULC feature returned.")

        time.sleep(0.5)