import geopandas as gpd
import pandas as pd
from pathlib import Path

HIGHWAY_FILE = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset"
    r"\GatiShakti_MORTH_National_Highways.geojsonl"
)

ROUTES = {
    "Route 1": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_1_corridor_2m.gpkg"
    ),
    "Route 2": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_2_corridor_2m.gpkg"
    ),
    "Route 3": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_3_corridor_2m.gpkg"
    ),
}

OUTPUT_DIR = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\results"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Combined route bounding box
BBOX = (
    72.8369,
    17.0434,
    78.4679,
    19.1907,
)

print("Loading highway dataset...")
highways = gpd.read_file(HIGHWAY_FILE, bbox=BBOX)

print(f"Highway candidates: {len(highways)}")

highways = highways.to_crs(32643)

summary = []
details = []

for route_name, route_file in ROUTES.items():

    print(f"\nProcessing {route_name}...")

    corridor = gpd.read_file(route_file).to_crs(32643)

    intersections = gpd.sjoin(
        highways,
        corridor,
        predicate="intersects",
        how="inner",
    )

    segment_count = len(intersections)

    valid_names = (
        intersections["road_name"]
        .dropna()
        .astype(str)
    )

    unique_road_count = valid_names.nunique()

    road_type_counts = (
        intersections["road_type"]
        .fillna("Unknown")
        .value_counts()
        .to_dict()
    )

    state_counts = (
        intersections["state_ut"]
        .fillna("Unknown")
        .value_counts()
        .to_dict()
    )

    summary.append({
        "route": route_name,
        "intersecting_segment_count": segment_count,
        "unique_road_count": unique_road_count,
        "road_type_counts": str(road_type_counts),
        "state_counts": str(state_counts),
    })

    cols = [
        "road_name",
        "road_type",
        "lane_statu",
        "state_ut",
        "gis_length",
        "category",
        "level_1",
        "level_2",
        "level_3",
        "level_4",
        "level_5",
        "status",
    ]

    available_cols = [
        c for c in cols
        if c in intersections.columns
    ]

    detail = intersections[available_cols].copy()
    detail.insert(0, "route", route_name)

    details.append(detail)

    print(f"Intersecting segments: {segment_count}")
    print(f"Unique named roads: {unique_road_count}")


summary_df = pd.DataFrame(summary)

details_df = pd.concat(
    details,
    ignore_index=True
)

summary_file = OUTPUT_DIR / "highway_impact_summary.csv"
details_file = OUTPUT_DIR / "highway_impact_details.csv"

summary_df.to_csv(summary_file, index=False)
details_df.to_csv(details_file, index=False)

print("\nCompleted.")
print(f"Summary: {summary_file}")
print(f"Details: {details_file}")

print("\nSummary:")
print(summary_df.to_string(index=False))