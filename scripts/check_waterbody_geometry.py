import geopandas as gpd
from pathlib import Path

SAROVAR = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"
)

sarovar = gpd.read_file(SAROVAR)

print()
print("=" * 60)
print("SAROVAR GEOMETRY VALIDATION")
print("=" * 60)

print("Total features:", len(sarovar))

print()
print("CRS:", sarovar.crs)

print()
print("Geometry types:")
print(sarovar.geom_type.value_counts())

print()
print("Null geometries:", sarovar.geometry.isna().sum())

print("Empty geometries:", sarovar.geometry.is_empty.sum())

print("Invalid geometries:", (~sarovar.geometry.is_valid).sum())

# Remove unusable geometries
valid = sarovar[
    sarovar.geometry.notna()
    & ~sarovar.geometry.is_empty
    & sarovar.geometry.is_valid
].copy()

print()
print("=" * 60)
print("USABLE GEOMETRIES")
print("=" * 60)

print("Usable features:", len(valid))
print("Removed features:", len(sarovar) - len(valid))