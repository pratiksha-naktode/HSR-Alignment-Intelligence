import requests
from pathlib import Path

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.3.0"
    "&request=GetLegendGraphic"
    "&format=image/png"
    "&width=30"
    "&height=30"
    "&layer=sisdp_lulc_v2"
)

output = Path(r"data\processed\bhuvan_sisdp_lulc_legend.png")
output.parent.mkdir(parents=True, exist_ok=True)

print("Downloading official Bhuvan LULC legend...")

try:
    response = requests.get(url, timeout=30)

    print("HTTP status:", response.status_code)
    print("Content type:", response.headers.get("Content-Type"))
    print("Size:", len(response.content), "bytes")

    if response.status_code == 200 and response.content:
        output.write_bytes(response.content)
        print("\nSaved to:")
        print(output.resolve())
    else:
        print("\nLegend download failed.")
        print(response.text[:500])

except Exception as e:
    print("\nERROR:")
    print(e)