import requests
from pathlib import Path

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.1.1"
    "&request=GetStyles"
    "&layers=MH_Latur_lulc_v2"
)

output = Path(r"data\processed\MH_Latur_lulc_v2.sld")

print("=" * 70)
print("SAVING OFFICIAL BHUVAN SLD")
print("=" * 70)

try:
    r = requests.get(url, timeout=60)

    print("HTTP status:", r.status_code)
    print("Content type:", r.headers.get("Content-Type"))
    print("Size:", len(r.content), "bytes")

    if r.status_code == 200 and b"<sld:" in r.content:
        output.write_bytes(r.content)
        print("\nSaved:")
        print(output.resolve())
    else:
        print("\nUnexpected response:")
        print(r.text[:1000])

except Exception as e:
    print("\nERROR:")
    print(e)