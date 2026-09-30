import geopandas as gpd
import os

BASE = r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
LULC = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\bhuvan 2\bhuvan 2.shp"

ROUTES = {
    "Route_1": os.path.join(BASE, "data", "processed", "Route_1_corridor_2m.gpkg"),
    "Route_2": os.path.join(BASE, "data", "processed", "Route_2_corridor_2m.gpkg"),
    "Route_3": os.path.join(BASE, "data", "processed", "Route_3_corridor_2m.gpkg"),
}

for route, corridor_path in ROUTES.items():

    print(f"\n========== {route} ==========")

    corridor = gpd.read_file(corridor_path).to_crs(4326)

    print("Reading Bhuvan candidates...")
    lulc = gpd.read_file(
        LULC,
        bbox=tuple(corridor.total_bounds),
        columns=["DN"]
    )

    print("Candidates:", len(lulc))

    lulc = lulc.to_crs(32643)
    corridor = corridor.to_crs(32643)

    print("Finding intersections...")

    intersected = gpd.sjoin(
        lulc,
        corridor,
        predicate="intersects",
        how="inner"
    )

    print("Intersecting polygons:", len(intersected))
    print("Unique DN:", intersected["DN"].nunique())

    print("\nDN counts:")
    print(intersected["DN"].value_counts().sort_index())

    out = os.path.join(
        BASE,
        "data",
        "processed",
        f"{route}_lulc_intersections.gpkg"
    )

    intersected.to_file(out, driver="GPKG")

    print("Saved:", out)