import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

HIGHWAYS = (
    BASE
    / "data"
    / "processed"
    / "highways_route_area.geojsonl"
)

RESULTS = BASE / "data" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Load filtered highway candidates
highways = gpd.read_file(HIGHWAYS)

print("Highway candidates:", len(highways))
print("CRS:", highways.crs)

# Reproject to metric CRS
highways = highways.to_crs("EPSG:32643")

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

    # Precise intersection
    intersecting = highways[highways.geometry.intersects(route_geometry)].copy()

    print()
    print(f"Route {route_no}")
    print("Intersecting highway segments:", len(intersecting))

    total_intersection_length = 0.0

    route_details = []

    for idx, row in intersecting.iterrows():

        intersection = row.geometry.intersection(route_geometry)

        if intersection.is_empty:
            continue

        intersection_length = intersection.length

        total_intersection_length += intersection_length

        route_details.append({
            "route": f"Route {route_no}",
            "highway_id": row.get("id"),
            "road_name": row.get("road_name"),
            "road_type": row.get("road_type"),
            "lane_status": row.get("lane_statu"),
            "category": row.get("category"),
            "status": row.get("status"),
            "gis_length_km": row.get("gis_length"),
            "intersection_length_m": intersection_length
        })

    summary.append({
        "route": f"Route {route_no}",
        "highway_segment_count": len(route_details),
        "total_highway_intersection_length_m": total_intersection_length,
        "total_highway_intersection_length_km": total_intersection_length / 1000
    })

    details.extend(route_details)

summary_df = pd.DataFrame(summary)
details_df = pd.DataFrame(details)

summary_path = RESULTS / "highway_intersection_summary.csv"
details_path = RESULTS / "highway_intersection_details.csv"

summary_df.to_csv(summary_path, index=False)
details_df.to_csv(details_path, index=False)

print()
print("========== HIGHWAY INTERSECTION SUMMARY ==========")
print(summary_df.to_string(index=False))

print()
print("Summary:", summary_path)
print("Details:", details_path)
