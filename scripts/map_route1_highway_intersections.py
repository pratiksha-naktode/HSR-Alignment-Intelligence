import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

# --------------------------------------------------
# Files
# --------------------------------------------------

CORRIDOR = (
    BASE
    / "data"
    / "processed"
    / "Route_1_corridor_2m.gpkg"
)

HIGHWAYS = (
    BASE
    / "data"
    / "processed"
    / "highways_route_area.geojsonl"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "route1_highway_intersection_map.png"
)

# --------------------------------------------------
# Load data
# --------------------------------------------------

corridor = gpd.read_file(CORRIDOR)

highways = gpd.read_file(HIGHWAYS)

# Use a metric CRS
corridor = corridor.to_crs("EPSG:32643")
highways = highways.to_crs("EPSG:32643")

route_geometry = corridor.geometry.iloc[0]

# --------------------------------------------------
# Find highway intersections
# --------------------------------------------------

intersections = highways[
    highways.geometry.intersects(route_geometry)
].copy()

intersections["intersection_length_m"] = (
    intersections.geometry
    .intersection(route_geometry)
    .length
)

# Only display large intersections
large = intersections[
    intersections["intersection_length_m"] >= 300
].copy()

# --------------------------------------------------
# Plot
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(14, 12))

# All intersecting highways
intersections.plot(
    ax=ax,
    linewidth=1,
    alpha=0.5
)

# Large intersections
large.plot(
    ax=ax,
    linewidth=3,
    alpha=0.9
)

# HSR corridor
corridor.plot(
    ax=ax,
    linewidth=2
)

ax.set_title(
    "Route 1 - HSR Corridor and Large Highway Intersections"
)

ax.set_axis_off()

plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print()
print("Large intersections:", len(large))
print("Map saved to:")
print(OUTPUT)