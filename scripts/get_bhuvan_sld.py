import requests

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.1.1"
    "&request=GetStyles"
    "&layers=MH_Latur_lulc_v2"
)

print("=" * 70)
print("REQUESTING BHUVAN LULC STYLE DEFINITION")
print("=" * 70)

try:
    r = requests.get(url, timeout=30)

    print("HTTP status:", r.status_code)
    print("Content type:", r.headers.get("Content-Type"))
    print("Response size:", len(r.content), "bytes")

    print("\nFirst 3000 characters:")
    print(r.text[:3000])

except Exception as e:
    print("ERROR:", e)