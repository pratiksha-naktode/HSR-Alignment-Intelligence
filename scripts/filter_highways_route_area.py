import json
from pathlib import Path
from shapely.geometry import shape, box
from shapely.strtree import STRtree
import geopandas as gpd

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\GatiShakti_MORTH_National_Highways.geojsonl"
)

OUTPUT = BASE / "data" / "processed" / "highways_route_area.geojsonl"

# Read route corridors in WGS84
corridors = []

for route_no in [1, 2, 3]:
    path = (
        BASE
        / "data"
        / "processed"
        / f"Route_{route_no}_corridor_2m.gpkg"
    )

    gdf = gpd.read_file(path).to_crs("EPSG:4326")
    corridors.append(gdf.geometry.iloc[0])

# Combined bounding box
combined = corridors[0]

for geom in corridors[1:]:
    combined = combined.union(geom)

route_bbox = box(*combined.bounds)

print("Route bounding box:")
print(route_bbox.bounds)
print()

count = 0
candidates = 0

with open(INPUT, "r", encoding="utf-8") as src, \
     open(OUTPUT, "w", encoding="utf-8") as dst:

    for line in src:

        if not line.strip():
            continue

        record = json.loads(line)

        geometry_data = record.get("geometry")

        if not geometry_data:
            continue

        geom = shape(geometry_data)

        # Fast bounding-box test
        if not geom.bounds:
            continue

        geom_bbox = box(*geom.bounds)

        if not geom_bbox.intersects(route_bbox):
            continue

        candidates += 1

        dst.write(json.dumps(record) + "\n")

        count += 1

        if count % 1000 == 0:
            print(f"Saved candidates: {count}")

print()
print("Total candidate highway segments:", count)
print("Output:", OUTPUT)
