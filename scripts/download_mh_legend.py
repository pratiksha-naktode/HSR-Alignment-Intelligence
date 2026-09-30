import requests
from pathlib import Path

layer = "MH_Latur_lulc_v2"

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.3.0"
    "&request=GetLegendGraphic"
    "&format=image/png"
    "&width=30"
    "&height=30"
    f"&layer={layer}"
)

output = Path(
    r"data\processed\bhuvan_mh_latur_lulc_legend.png"
)

print("Requesting:", layer)

try:
    response = requests.get(url, timeout=30)

    print("HTTP status:", response.status_code)
    print("Content type:", response.headers.get("Content-Type"))
    print("Size:", len(response.content), "bytes")

    if (
        response.status_code == 200
        and response.headers.get("Content-Type", "").lower().startswith("image/")
    ):
        output.write_bytes(response.content)

        print("\nSUCCESS")
        print("Saved:", output.resolve())

    else:
        print("\nSERVER RESPONSE:")
        print(response.text[:1000])

except Exception as e:
    print("\nERROR:")
    print(e)