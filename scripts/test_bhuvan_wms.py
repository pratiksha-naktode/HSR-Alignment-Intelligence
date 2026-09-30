import requests

url = "https://bhuvanpanchayat.nrsc.gov.in/geoserver2/SISDP_P2/wms"

params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetCapabilities"
}

r = requests.get(url, params=params, timeout=30)

print("Status:", r.status_code)
print("Size:", len(r.content))
print("URL:", r.url)

open("data/processed/bhuvan_p2_capabilities.xml", "wb").write(r.content)

print("Saved capabilities file.")