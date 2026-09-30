import geopandas as gpd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

SAROVAR = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"
)

sarovar = gpd.read_file(SAROVAR).to_crs("EPSG:32643")

# Remove empty geometries
sarovar = sarovar[sarovar.geometry.notna()].copy()

print("Valid Sarovars:", len(sarovar))
print()

for route_no in [1, 2, 3]:

    corridor_path = (
        BASE
        / "data"
        / "processed"
        / f"Route_{route_no}_corridor_2m.gpkg"
    )

    corridor = gpd.read_file(corridor_path).to_crs("EPSG:32643")

    route_geometry = corridor.geometry.iloc[0]

    distances = sarovar.geometry.distance(route_geometry)

    within_10m = (distances <= 10).sum()
    within_50m = (distances <= 50).sum()
    within_100m = (distances <= 100).sum()

    print(f"Route {route_no}")
    print(f"  Within 10 m : {within_10m}")
    print(f"  Within 50 m : {within_50m}")
    print(f"  Within 100 m: {within_100m}")
    print()

