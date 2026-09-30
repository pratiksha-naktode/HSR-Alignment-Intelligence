import geopandas as gpd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT")
OUT = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed")
OUT.mkdir(parents=True, exist_ok=True)

routes = {
    "Route_1": BASE / "RouteData" / "R1" / "R1" / "ROUTE 1.shp",
    "Route_2": BASE / "RouteData" / "R2" / "R2" / "ROUTE 2.shp",
    "Route_3": BASE / "RouteData" / "R3" / "R3" / "ROUTE 3.shp",
}

# Metric CRS suitable for the route area
METRIC_CRS = "EPSG:32643"

for name, path in routes.items():
    gdf = gpd.read_file(path)

    # Source data is WGS84
    gdf = gdf.to_crs(METRIC_CRS)

    # 2 m total width = 1 m on each side
    corridor = gdf.copy()
    corridor["geometry"] = corridor.geometry.buffer(1.0)

    # Save both centerline and corridor
    gdf.to_file(OUT / f"{name}_centerline.gpkg", driver="GPKG")
    corridor.to_file(OUT / f"{name}_corridor_2m.gpkg", driver="GPKG")

    print(
        f"{name}: "
        f"length={gdf.geometry.length.sum():,.2f} m, "
        f"corridor_area={corridor.geometry.area.sum():,.2f} m2"
    )

print("\nDone.")
