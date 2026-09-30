import rasterio
from pathlib import Path

p = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata")

files = [
    p / "LULC_bhuvan.tif",
    p / "LULC_BHUVAN2.tif",
    p / "New folder.tif",
]

for x in files:
    print("\n===", x.name, "===")

    with rasterio.open(x) as src:
        print("CRS:", src.crs)
        print("Size:", src.width, "x", src.height)
        print("Bands:", src.count)
        print("Dtype:", src.dtypes)
        print("Nodata:", src.nodata)
        print("Bounds:", src.bounds)
        print("Resolution:", src.res)
        print("Tags:", src.tags())
