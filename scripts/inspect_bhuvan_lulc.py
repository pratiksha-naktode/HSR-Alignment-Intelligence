from pathlib import Path
import geopandas as gpd

BASE = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT")
LULC = BASE / "landuseddata" / "bhuvan 2" / "bhuvan 2.shp"

print("=" * 70)
print("BHUVAN LULC DATA INSPECTION")
print("=" * 70)

print(f"\nFile: {LULC}")
print(f"Exists: {LULC.exists()}")

if not LULC.exists():
    print("\nERROR: Bhuvan 2 shapefile not found.")
    raise SystemExit(1)

print("\nReading shapefile metadata...")
gdf = gpd.read_file(LULC, rows=5)

print("\nCRS:")
print(gdf.crs)

print("\nColumns:")
print(list(gdf.columns))

print("\nSample records:")
print(gdf[["DN", "geometry"]].head())

print("\nGeometry type:")
print(gdf.geometry.geom_type.value_counts())

print("\nDN datatype:")
print(gdf["DN"].dtype)

print("\nSample DN values:")
print(sorted(gdf["DN"].dropna().unique().tolist()))

print("\n" + "=" * 70)
print("IMPORTANT")
print("=" * 70)
print("""
The local Bhuvan shapefile contains DN values only.
This script intentionally does NOT assume that DN values represent
Forest, Agriculture, Built-up, etc.

The official Bhuvan Panchayat documentation confirms that SISDP
LULC data can be accessed as shapefiles and through OGC WMS/WMTS
services. The class mapping must therefore be verified from the
official Bhuvan classification/source rather than guessed.
""")

print("=" * 70)