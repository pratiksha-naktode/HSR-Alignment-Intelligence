import requests
import xml.etree.ElementTree as ET

layer = "MH_Latur_lulc_v2"

url = (
    "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/ows"
    "?service=WMS"
    "&version=1.1.1"
    "&request=GetStyles"
    f"&layers={layer}"
)

print("=" * 80)
print("BHUVAN OFFICIAL LULC CLASS / CODE TABLE")
print("=" * 80)

response = requests.get(url, timeout=30)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "sld": "http://www.opengis.net/sld",
    "ogc": "http://www.opengis.net/ogc"
}

rows = []

for rule in root.findall(".//sld:Rule", ns):

    name = rule.findtext("sld:Name", default="", namespaces=ns)
    title = rule.findtext("sld:Title", default="", namespaces=ns)

    codes = []

    for literal in rule.findall(".//ogc:Literal", ns):
        value = literal.text

        if value:
            value = value.strip()

            # LULC codes are alphabetic codes such as BUUR, AGRI, etc.
            if value.isalpha():
                codes.append(value)

    codes = sorted(set(codes))

    if title:
        rows.append((name, title, codes))

for name, title, codes in rows:

    print("\n" + "-" * 80)
    print(f"Rule : {name}")
    print(f"Class: {title}")
    print("Codes:", ", ".join(codes))

print("\n" + "=" * 80)
print("TOTAL CLASSES:", len(rows))
print("=" * 80)