from pathlib import Path
import zipfile
import sqlite3
import re

QGZ = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\main file gis all.qgz")

print("=" * 70)
print("SEARCHING QGIS STYLE DATABASE FOR DN CLASSIFICATION")
print("=" * 70)

with zipfile.ZipFile(QGZ, "r") as z:
    names = z.namelist()

    db_files = [n for n in names if n.lower().endswith(".db")]

    print("\nStyle databases:")
    for db in db_files:
        print(" -", db)

    if not db_files:
        print("No style database found.")
        raise SystemExit

    db_data = z.read(db_files[0])

temp = Path("data/processed/MxlAiN_styles_temp.db")
temp.parent.mkdir(parents=True, exist_ok=True)
temp.write_bytes(db_data)

conn = sqlite3.connect(temp)
cur = conn.cursor()

cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)

tables = [row[0] for row in cur.fetchall()]

print("\nTables:")
for table in tables:
    print(" -", table)

keywords = [
    "DN",
    "Forest",
    "Agriculture",
    "Built",
    "Urban",
    "LULC",
    "Crop",
    "Fallow",
]

print("\n" + "=" * 70)
print("SEARCHING SYMBOL NAMES AND XML")
print("=" * 70)

if "symbol" in tables:
    cur.execute("SELECT id, name, xml FROM symbol")

    matches = 0

    for symbol_id, name, xml in cur.fetchall():

        text = f"{name or ''}\n{xml or ''}"

        if any(
            re.search(rf"\b{re.escape(k)}\b", text, re.IGNORECASE)
            for k in keywords
        ):
            matches += 1

            print("\n" + "-" * 70)
            print("ID:", symbol_id)
            print("NAME:", name)

            # Print only useful snippets
            for pattern in keywords:
                found = re.search(
                    rf".{{0,150}}{re.escape(pattern)}.{{0,300}}",
                    text,
                    re.IGNORECASE
                )

                if found:
                    print("MATCH:", found.group(0))

    print("\nTotal matching symbols:", matches)

else:
    print("symbol table not found.")

conn.close()

print("\n" + "=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)