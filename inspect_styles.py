import zipfile
import sqlite3
import os

qgz = r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\main file gis all.qgz"
out = r"data\processed\MxlAiN_styles.db"

with zipfile.ZipFile(qgz) as z:
    with open(out, "wb") as f:
        f.write(z.read("MxlAiN_styles.db"))

con = sqlite3.connect(out)

tables = con.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables:")
for table in tables:
    print(" -", table[0])

con.close()

print("\nSaved:", os.path.abspath(out))