import requests

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.1.1"
    "&request=GetFeatureInfo"
    "&layers=MH_Latur_lulc_v2"
    "&query_layers=MH_Latur_lulc_v2"
    "&info_format=application/json"
    "&srs=EPSG:4326"
    "&bbox=75.5,17.5,76.0,18.0"
    "&width=500"
    "&height=500"
    "&x=250"
    "&y=250"
)

print("=" * 70)
print("BHUVAN WMS GETFEATUREINFO TEST")
print("=" * 70)

try:
    r = requests.get(url, timeout=30)

    print("HTTP status:", r.status_code)
    print("Content type:", r.headers.get("Content-Type"))
    print("Response size:", len(r.content), "bytes")

    print("\nResponse:")
    print(r.text[:5000])

except Exception as e:
    print("ERROR:", e)