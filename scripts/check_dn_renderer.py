from pathlib import Path
import zipfile
import re

qgz = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\main file gis all.qgz"
)

with zipfile.ZipFile(qgz, "r") as z:
    qgs_files = [x for x in z.namelist() if x.lower().endswith(".qgs")]

    if not qgs_files:
        print("QGS file not found")
        raise SystemExit

    qgs = z.read(qgs_files[0]).decode("utf-8", errors="ignore")

print("=" * 70)
print("CHECKING QGIS DN RENDERER")
print("=" * 70)

patterns = [
    r'attr="DN"',
    r"attr='DN'",
    r"categorizedSymbol",
    r"graduatedSymbol",
    r"<category",
    r"<renderer-v2",
]

for pattern in patterns:
    matches = list(re.finditer(pattern, qgs, re.IGNORECASE))

    print(f"\n{pattern}: {len(matches)} matches")

    for m in matches[:10]:
        start = max(0, m.start() - 300)
        end = min(len(qgs), m.end() + 800)

        print("-" * 60)
        print(qgs[start:end].replace("\n", " ")[:1200])

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)