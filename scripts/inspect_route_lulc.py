import geopandas as gpd
from pathlib import Path

files = {
    "Route 1": r"data\processed\Route_1_lulc_intersections.gpkg",
    "Route 2": r"data\processed\Route_2_lulc_intersections.gpkg",
    "Route 3": r"data\processed\Route_3_lulc_intersections.gpkg",
}

print("=" * 80)
print("ROUTE-SPECIFIC BHUVAN LULC DATA")
print("=" * 80)

for route, path in files.items():

    print(f"\n{'-' * 80}")
    print(route)

    gdf = gpd.read_file(path)

    print("Features:", len(gdf))
    print("CRS:", gdf.crs)
    print("Columns:", list(gdf.columns))
    print("Geometry:", gdf.geometry.geom_type.value_counts().to_dict())

    print("\nDN statistics:")
    print("Unique DN:", gdf["DN"].nunique())
    print("Minimum:", gdf["DN"].min())
    print("Maximum:", gdf["DN"].max())

    print("\nFirst 20 DN values:")
    print(sorted(gdf["DN"].unique())[:20])

    print("\nSample:")
    print(gdf[["DN", "geometry"]].head(3).to_string(index=False))

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)