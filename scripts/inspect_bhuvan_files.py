from pathlib import Path

folder = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\bhuvan 2")

print("=" * 70)
print("BHUVAN 2 FILES")
print("=" * 70)

for p in folder.iterdir():
    print(f"{p.name:40} {p.stat().st_size:,} bytes")

print("\n" + "=" * 70)
print("PRJ CONTENT")
print("=" * 70)

prj = folder / "bhuvan 2.prj"

if prj.exists():
    print(prj.read_text(errors="ignore"))
else:
    print("PRJ file not found.")

print("\n" + "=" * 70)
print("DBF HEADER")
print("=" * 70)

dbf = folder / "bhuvan 2.dbf"

with open(dbf, "rb") as f:
    header = f.read(32)

print("Header bytes:", header.hex())
print("Record count:", int.from_bytes(header[4:8], "little"))
print("Header length:", int.from_bytes(header[8:10], "little"))
print("Record length:", int.from_bytes(header[10:12], "little"))

print("\nField descriptors:")

with open(dbf, "rb") as f:
    f.seek(32)

    while True:
        field = f.read(32)

        if not field or field[0] == 0x0D:
            break

        name = field[:11].split(b"\x00")[0].decode(
            "ascii", errors="ignore"
        )

        field_type = chr(field[11])
        length = field[16]
        decimals = field[17]

        print(
            f"Name={name}, "
            f"Type={field_type}, "
            f"Length={length}, "
            f"Decimals={decimals}"
        )

print("\nDONE")