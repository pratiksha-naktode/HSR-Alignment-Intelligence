import rasterio
from pathlib import Path

p = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata")

for name in ["LULC_bhuvan.tif", "LULC_BHUVAN2.tif", "New folder.tif"]:
    path = p / name

    print("\n===", name, "===")

    with rasterio.open(path) as src:
        for i in range(1, src.count + 1):
            print(
                "Band", i,
                "| description:", src.descriptions[i-1],
                "| tags:", src.tags(i)
            )
