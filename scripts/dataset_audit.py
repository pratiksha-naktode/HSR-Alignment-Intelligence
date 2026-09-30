from pathlib import Path
import geopandas as gpd
import rasterio


# ============================================================
# DATASET LOCATION
# ============================================================

DATA_ROOT = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT")


# ============================================================
# VECTOR AUDIT
# ============================================================

def audit_vector(path):

    print("\n" + "=" * 80)
    print(f"VECTOR FILE: {path.name}")
    print("=" * 80)

    try:
        gdf = gpd.read_file(path)

        print(f"Path          : {path}")
        print(f"Feature count : {len(gdf)}")
        print(f"CRS           : {gdf.crs}")

        print("\nGeometry types:")
        print(gdf.geometry.geom_type.value_counts())

        print("\nColumns:")
        for column in gdf.columns:
            print(f"  {column}")

        print("\nBounds:")
        print(gdf.total_bounds)

        print("\nNull geometries:")
        print(gdf.geometry.isna().sum())

        print("\nInvalid geometries:")
        print((~gdf.geometry.is_valid).sum())

        print("\nFirst 3 records:")
        print(gdf.head(3))

    except Exception as error:
        print(f"ERROR READING FILE:")
        print(error)


# ============================================================
# RASTER AUDIT
# ============================================================

def audit_raster(path):

    print("\n" + "=" * 80)
    print(f"RASTER FILE: {path.name}")
    print("=" * 80)

    try:

        with rasterio.open(path) as src:

            print(f"Path          : {path}")
            print(f"CRS           : {src.crs}")
            print(f"Width         : {src.width}")
            print(f"Height        : {src.height}")
            print(f"Bands         : {src.count}")
            print(f"Data types    : {src.dtypes}")
            print(f"Resolution    : {src.res}")
            print(f"Bounds        : {src.bounds}")
            print(f"NoData        : {src.nodata}")

    except Exception as error:
        print("ERROR READING RASTER:")
        print(error)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 80)
    print("       HSR ROUTE OPTIMIZATION - DATASET AUDIT")
    print("=" * 80)

    print(f"\nDataset location:")
    print(DATA_ROOT)

    if not DATA_ROOT.exists():

        print("\nERROR:")
        print("Dataset directory does not exist.")

        return

    print("\nDataset directory found successfully.")

    # --------------------------------------------------------
    # VECTOR FILES
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 80)
    print("VECTOR DATASETS")
    print("=" * 80)

    vector_extensions = {
        ".shp",
        ".geojson",
        ".geojsonl",
        ".gpkg"
    }

    vector_files = []

    for file in DATA_ROOT.rglob("*"):

        if (
            file.is_file()
            and file.suffix.lower() in vector_extensions
        ):
            vector_files.append(file)

    print(f"\nTotal vector files found: {len(vector_files)}")

    for file in vector_files:

        # GeoJSONL can be very large.
        # We will inspect it separately later.
        if file.suffix.lower() == ".geojsonl":

            print("\n" + "-" * 80)
            print(f"GEOJSONL FILE: {file.name}")
            print("-" * 80)

            size_mb = file.stat().st_size / (1024 * 1024)

            print(f"Path : {file}")
            print(f"Size : {size_mb:.2f} MB")
            print("Detailed inspection: PENDING")

        else:

            audit_vector(file)

    # --------------------------------------------------------
    # RASTER FILES
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 80)
    print("RASTER DATASETS")
    print("=" * 80)

    raster_extensions = {
        ".tif",
        ".tiff"
    }

    raster_files = []

    for file in DATA_ROOT.rglob("*"):

        if (
            file.is_file()
            and file.suffix.lower() in raster_extensions
        ):
            raster_files.append(file)

    print(f"\nTotal raster files found: {len(raster_files)}")

    for file in raster_files:

        audit_raster(file)

    # --------------------------------------------------------
    # QGIS PROJECT
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 80)
    print("QGIS PROJECT FILES")
    print("=" * 80)

    qgis_files = list(DATA_ROOT.rglob("*.qgz"))

    print(f"\nQGIS projects found: {len(qgis_files)}")

    for file in qgis_files:

        size_mb = file.stat().st_size / (1024 * 1024)

        print(f"\nFile: {file}")
        print(f"Size: {size_mb:.2f} MB")

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 80)
    print("                 AUDIT COMPLETE")
    print("=" * 80)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()