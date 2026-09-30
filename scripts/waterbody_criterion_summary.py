import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

SAROVAR = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "waterbody_criterion_summary.csv"
)

# --------------------------------------------------
# Load Sarovar dataset
# --------------------------------------------------

sarovar = gpd.read_file(SAROVAR)

sarovar = sarovar[
    sarovar.geometry.notna()
    & ~sarovar.geometry.is_empty
    & sarovar.geometry.is_valid
].copy()

sarovar = sarovar.to_crs("EPSG:32643")

print("Usable Sarovar features:", len(sarovar))

# --------------------------------------------------
# Analyze each route
# --------------------------------------------------

results = []

for route_no in [1, 2, 3]:

    corridor_path = (
        BASE
        / "data"
        / "processed"
        / f"Route_{route_no}_corridor_2m.gpkg"
    )

    corridor = gpd.read_file(corridor_path).to_crs("EPSG:32643")

    route_geometry = corridor.geometry.iloc[0]

    # Distance from every Sarovar to route corridor
    distances = sarovar.geometry.distance(route_geometry)

    # Remove any unexpected non-finite values
    distances = distances[distances.notna()]

    nearest_distance = distances.min()

    within_10 = (distances <= 10).sum()
    within_50 = (distances <= 50).sum()
    within_100 = (distances <= 100).sum()
    within_250 = (distances <= 250).sum()
    within_500 = (distances <= 500).sum()

    results.append({
        "route": f"Route {route_no}",
        "nearest_waterbody_distance_m": nearest_distance,
        "waterbodies_within_10m": within_10,
        "waterbodies_within_50m": within_50,
        "waterbodies_within_100m": within_100,
        "waterbodies_within_250m": within_250,
        "waterbodies_within_500m": within_500
    })

# --------------------------------------------------
# Create summary
# --------------------------------------------------

summary = pd.DataFrame(results)

summary[
    [
        "nearest_waterbody_distance_m",
    ]
] = summary[
    [
        "nearest_waterbody_distance_m",
    ]
].round(2)

print()
print("=" * 80)
print("WATERBODY CRITERION SUMMARY")
print("=" * 80)

print(
    summary.to_string(index=False)
)

# --------------------------------------------------
# Save
# --------------------------------------------------

summary.to_csv(
    OUTPUT,
    index=False
)

print()
print("Saved to:")
print(OUTPUT)