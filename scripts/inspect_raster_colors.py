import rasterio
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata")

files = [
    BASE / "LULC_bhuvan.tif",
    BASE / "LULC_BHUVAN2.tif",
    BASE / "New folder.tif",
]

for path in files:
    print("\n" + "=" * 70)
    print(path.name)
    print("=" * 70)

    with rasterio.open(path) as src:
        print("Size:", src.width, "x", src.height)
        print("CRS:", src.crs)
        print("Dtype:", src.dtypes)
        print("Bands:", src.count)

        # Read a representative window instead of the entire huge raster
        w = min(2000, src.width)
        h = min(2000, src.height)

        data = src.read(
            [1, 2, 3, 4],
            window=((0, h), (0, w))
        )

        pixels = list(zip(
            data[0].ravel(),
            data[1].ravel(),
            data[2].ravel(),
            data[3].ravel()
        ))

        counts = Counter(pixels)

        print("Unique RGBA values in sample:", len(counts))

        print("\nMost common RGBA values:")
        for rgba, count in counts.most_common(30):
            print(rgba, "=>", count)

        print("\nBand ranges:")
        for i in range(4):
            print(
                f"Band {i+1}:",
                int(data[i].min()),
                "to",
                int(data[i].max())
            )