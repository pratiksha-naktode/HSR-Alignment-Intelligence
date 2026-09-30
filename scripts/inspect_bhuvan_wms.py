import urllib.request

url = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/wms?service=WMS&request=GetCapabilities"

data = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "ignore")

with open(
    r".\data\processed\bhuvan_wms_capabilities.xml",
    "w",
    encoding="utf-8"
) as f:
    f.write(data)

keywords = [
    "LULC",
    "Land Use",
    "Land Cover",
    "Agriculture",
    "Built",
    "Forest",
    "SISDP"
]

print("Saved capabilities XML.")
print("Length:", len(data))
print()

for keyword in keywords:
    print(f"===== {keyword} =====")

    start = 0
    found = 0

    while True:
        pos = data.lower().find(keyword.lower(), start)

        if pos == -1:
            break

        print(data[max(0, pos-300):pos+500])
        print()
        
        found += 1
        start = pos + len(keyword)

        if found >= 5:
            break

    print("Matches shown:", found)
    print()

