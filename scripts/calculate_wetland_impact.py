import geopandas as gpd
import pandas as pd
from pathlib import Path

PROJECT = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

WETLANDS = PROJECT / "data" / "processed" / "wetlands_route_area.geojsonl"
ROUTES = PROJECT / "data" / "processed"

OUTPUT = PROJECT / "data" / "results"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("Loading filtered wetlands...")
wetlands = gpd.read_file(WETLANDS)

print("Wetlands loaded:", len(wetlands))
print("Wetland CRS:", wetlands.crs)

# Project wetlands to the same metric CRS as route corridors
wetlands = wetlands.to_crs("EPSG:32643")

route_results = []
detail_results = []

for route_no in [1, 2, 3]:

    route_file = ROUTES / f"Route_{route_no}_corridor_2m.gpkg"

    print(f"\nProcessing Route {route_no}...")

    route = gpd.read_file(route_file)

    if route.crs != wetlands.crs:
        route = route.to_crs(wetlands.crs)

    corridor = route.geometry.iloc[0]

    # Spatial candidate filtering
    candidates = wetlands[wetlands.intersects(corridor)].copy()

    print("Actual intersecting wetlands:", len(candidates))

    if len(candidates) == 0:
        route_results.append({
            "route": f"Route {route_no}",
            "wetland_count": 0,
            "wetland_area_m2": 0.0,
            "wetland_area_ha": 0.0,
        })
        continue

    # Actual geometric intersection
    candidates["intersection_geometry"] = candidates.geometry.intersection(
        corridor
    )

    candidates["intersection_area_m2"] = (
        candidates["intersection_geometry"].area
    )

    candidates = candidates[
        candidates["intersection_area_m2"] > 0
    ].copy()

    # Save detailed records
    for _, row in candidates.iterrows():
        detail_results.append({
            "route": f"Route {route_no}",
            "wetbnd_id": row["wetbnd_id"],
            "wetname": row["wetname"],
            "level1": row["level1"],
            "level2": row["level2"],
            "level3": row["level3"],
            "descr": row["descr"],
            "intersection_area_m2": row["intersection_area_m2"],
            "intersection_area_ha": row["intersection_area_m2"] / 10000,
        })

    total_area = candidates["intersection_area_m2"].sum()

    route_results.append({
        "route": f"Route {route_no}",
        "wetland_count": len(candidates),
        "wetland_area_m2": total_area,
        "wetland_area_ha": total_area / 10000,
    })

summary = pd.DataFrame(route_results)
details = pd.DataFrame(detail_results)

summary_file = OUTPUT / "wetland_impact_summary.csv"
detail_file = OUTPUT / "wetland_impact_details.csv"

summary.to_csv(summary_file, index=False)
details.to_csv(detail_file, index=False)

print("\n========================================")
print("WETLAND IMPACT RESULTS")
print("========================================")
print(summary.to_string(index=False))

print("\nSaved:")
print(summary_file)
print(detail_file)