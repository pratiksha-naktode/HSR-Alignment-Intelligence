import requests
from pathlib import Path

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.1.1"
    "&request=GetMap"
    "&layers=MH_Latur_lulc_v2"
    "&styles=sisdp_lulc_v2"
    "&format=image/png"
    "&srs=EPSG:4326"
    "&bbox=75.5,17.5,76.0,18.0"
    "&width=1000"
    "&height=1000"
)

output = Path(r"data\processed\bhuvan_latur_test.png")

print("=" * 70)
print("BHUVAN WMS GETMAP TEST")
print("=" * 70)

try:
    r = requests.get(url, timeout=60)

    print("HTTP status:", r.status_code)
    print("Content type:", r.headers.get("Content-Type"))
    print("Size:", len(r.content), "bytes")

    if (
        r.status_code == 200
        and r.headers.get("Content-Type", "").lower().startswith("image/")
    ):
        output.write_bytes(r.content)
        print("\nSUCCESS")
        print("Saved:", output.resolve())
    else:
        print("\nSERVER RESPONSE:")
        print(r.text[:1000])

except Exception as e:
    print("\nERROR:", e)