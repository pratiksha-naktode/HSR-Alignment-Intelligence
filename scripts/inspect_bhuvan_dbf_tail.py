from pathlib import Path

dbf = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\landuseddata\bhuvan 2\bhuvan 2.dbf")

print("=" * 70)
print("INSPECTING BHUVAN 2 DBF TAIL")
print("=" * 70)

if not dbf.exists():
    print("DBF NOT FOUND:", dbf)
    raise SystemExit

with open(dbf, "rb") as f:
    data = f.read()

print("Total DBF size:", len(data), "bytes")

# DBF header tells us where records start and their length.
header_length = int.from_bytes(data[8:10], "little")
record_length = int.from_bytes(data[10:12], "little")
record_count = int.from_bytes(data[4:8], "little")

print("Header length:", header_length)
print("Record length:", record_length)
print("Record count:", record_count)

records_end = header_length + (record_count * record_length)

print("Expected records end:", records_end)
print("Actual file size:", len(data))
print("Bytes after records:", len(data) - records_end)

print("\nLAST 512 BYTES:")
print(data[-512:])

print("\nHEX OF LAST 512 BYTES:")
print(data[-512:].hex())

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)
