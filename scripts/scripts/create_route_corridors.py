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

# ============================================================
# HSR PROJECT ASSUMPTIONS
# ============================================================

# Total ground footprint used for land-impact calculations
GROUND_FOOTPRINT_M = 3.5

# Half-width on each side of the centerline
BUFFER_DISTANCE_M = GROUND_FOOTPRINT_M / 2

# Metric CRS suitable for the route area
METRIC_CRS = "EPSG:32643"

print("=" * 70)
print("HSR ROUTE CORRIDOR GENERATION")
print("=" * 70)

print(f"\nGround footprint: {GROUND_FOOTPRINT_M} m")
print(f"Buffer on each side: {BUFFER_DISTANCE_M} m")
print(f"CRS: {METRIC_CRS}")

for name, path in routes.items():

    print(f"\nProcessing {name}...")
    print(f"Input: {path}")

    # Read centerline
    gdf = gpd.read_file(path)

    # Convert to metric CRS
    gdf = gdf.to_crs(METRIC_CRS)

    # Create 3.5 m total ground footprint
    corridor = gdf.copy()
    corridor["geometry"] = corridor.geometry.buffer(
        BUFFER_DISTANCE_M
    )

    # Save centerline
    centerline_output = OUT / f"{name}_centerline.gpkg"

    gdf.to_file(
        centerline_output,
        driver="GPKG"
    )

    # Save new 3.5 m corridor
    corridor_output = OUT / f"{name}_corridor_3_5m.gpkg"

    corridor.to_file(
        corridor_output,
        driver="GPKG"
    )

    # Calculate diagnostic values
    route_length_m = gdf.geometry.length.sum()
    corridor_area_m2 = corridor.geometry.area.sum()

    print(
        f"{name}: "
        f"length={route_length_m:,.2f} m, "
        f"corridor_area={corridor_area_m2:,.2f} m²"
    )

    print(f"Saved: {corridor_output}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)