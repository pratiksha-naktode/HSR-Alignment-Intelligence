from pathlib import Path
import zipfile
import re

QGZ = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\main file gis all.qgz")

print("=" * 70)
print("CHECKING QGIS PROJECT FOR BHUVAN DN CLASS MAPPING")
print("=" * 70)

if not QGZ.exists():
    print("QGZ NOT FOUND:", QGZ)
    raise SystemExit

with zipfile.ZipFile(QGZ, "r") as z:
    files = z.namelist()
    print("\nFiles inside QGZ:")
    for f in files:
        print(" -", f)

    qgs_files = [f for f in files if f.lower().endswith(".qgs")]

    if not qgs_files:
        print("\nNo QGS project found.")
        raise SystemExit

    qgs = z.read(qgs_files[0]).decode("utf-8", errors="ignore")

print("\nQGS project loaded.")

patterns = [
    "bhuvan 1",
    "bhuvan 2",
    "bhuvan 3",
    "DN",
    "Forest",
    "Agriculture",
    "Built",
    "Urban",
    "landuse",
    "lulc"
]

for pattern in patterns:
    print("\n" + "-" * 70)
    print("SEARCH:", pattern)

    matches = list(re.finditer(pattern, qgs, re.IGNORECASE))

    print("Matches:", len(matches))

    for m in matches[:5]:
        start = max(0, m.start() - 500)
        end = min(len(qgs), m.end() + 1000)
        print("\n", qgs[start:end])

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)