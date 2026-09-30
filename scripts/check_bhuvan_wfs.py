import requests

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WFS"
    "&version=1.1.0"
    "&request=GetCapabilities"
)

print("=" * 70)
print("BHUVAN WFS CHECK")
print("=" * 70)

try:
    r = requests.get(url, timeout=30)

    print("HTTP status:", r.status_code)
    print("Content type:", r.headers.get("Content-Type"))
    print("Response size:", len(r.content), "bytes")

    text = r.text

    print("\nContains WFS:", "WFS_Capabilities" in text)
    print("Contains lc_code:", "lc_code" in text)
    print("Contains Latur:", "Latur" in text)

    print("\nFirst 2000 characters:")
    print(text[:2000])

except Exception as e:
    print("ERROR:", e)