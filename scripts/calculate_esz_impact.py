import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

ESZ_PATH = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Bharatmaps_Parivesh_Eco_Sensitive_Zones.geojsonl\Bharatmaps_Parivesh_Eco_Sensitive_Zones.geojsonl"
)

RESULTS = BASE / "data" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Load ESZ polygons
esz = gpd.read_file(ESZ_PATH)

print("ESZ features:", len(esz))
print("CRS:", esz.crs)
print("Geometry:", esz.geom_type.value_counts().to_dict())

# Reproject to metric CRS
esz = esz.to_crs("EPSG:32643")

# Remove empty geometries
esz = esz[esz.geometry.notna() & ~esz.geometry.is_empty].copy()

summary = []
details = []

for route_no in [1, 2, 3]:

    corridor_path = (
        BASE
        / "data"
        / "processed"
        / f"Route_{route_no}_corridor_2m.gpkg"
    )

    corridor = gpd.read_file(corridor_path).to_crs("EPSG:32643")

    route_geometry = corridor.geometry.iloc[0]

    # ESZs directly intersecting the corridor
    intersecting = esz[esz.geometry.intersects(route_geometry)].copy()

    # Distance from every ESZ to route corridor
    distances = esz.geometry.distance(route_geometry)

    nearest_index = distances.idxmin()
    nearest_distance = distances.loc[nearest_index]
    nearest = esz.loc[nearest_index]

    summary.append({
        "route": f"Route {route_no}",
        "intersecting_esz_count": len(intersecting),
        "nearest_esz_distance_m": nearest_distance,
        "nearest_esz_name": nearest.get("Name"),
        "nearest_esz_zone_type": nearest.get("Zone_Type"),
        "nearest_esz_map_name": nearest.get("Map_Name"),
    })

    # Save the closest ESZs for detailed inspection
    closest_indices = distances.nsmallest(10).index

    for idx in closest_indices:
        row = esz.loc[idx]

        details.append({
            "route": f"Route {route_no}",
            "distance_m": distances.loc[idx],
            "Name": row.get("Name"),
            "Zone_Type": row.get("Zone_Type"),
            "Map_Name": row.get("Map_Name"),
            "Sub_Zone_T": row.get("Sub_Zone_T"),
            "Main_Zone_": row.get("Main_Zone_"),
            "Page_No": row.get("Page_No"),
        })

summary_df = pd.DataFrame(summary)
details_df = pd.DataFrame(details)

summary_path = RESULTS / "esz_impact_summary.csv"
details_path = RESULTS / "esz_nearest_details.csv"

summary_df.to_csv(summary_path, index=False)
details_df.to_csv(details_path, index=False)

print()
print("========== ESZ SUMMARY ==========")
print(summary_df.to_string(index=False))

print()
print("Summary saved to:", summary_path)
print("Details saved to:", details_path)
