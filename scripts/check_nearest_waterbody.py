import geopandas as gpd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

SAROVAR = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"
)

# Load Sarovar points
sarovar = gpd.read_file(SAROVAR).to_crs("EPSG:32643")

print("Total Sarovars:", len(sarovar))
print()

for route_no in [1, 2, 3]:

    corridor_path = (
        BASE
        / "data"
        / "processed"
        / f"Route_{route_no}_corridor_2m.gpkg"
    )

    corridor = gpd.read_file(corridor_path).to_crs("EPSG:32643")

    # Corridor is one polygon
    route_geometry = corridor.geometry.iloc[0]

    # Distance from every Sarovar point to the route corridor
    distances = sarovar.geometry.distance(route_geometry)

    nearest_distance = distances.min()

    nearest_index = distances.idxmin()
    nearest_sarovar = sarovar.loc[nearest_index]

    print(f"Route {route_no}")
    print(f"  Nearest Sarovar distance: {nearest_distance:.2f} m")
    print(f"  Sarovar ID: {nearest_sarovar['Sarovar_ID']}")
    print(f"  Name: {nearest_sarovar['Name_of_Sarovar']}")
    print(f"  Village: {nearest_sarovar['Village']}")
    print(f"  District: {nearest_sarovar['District']}")
    print(f"  State: {nearest_sarovar['State']}")
    print()

