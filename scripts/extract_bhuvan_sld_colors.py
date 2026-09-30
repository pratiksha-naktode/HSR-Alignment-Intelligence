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

print("=" * 90)
print("BHUVAN LULC CLASS -> CODE -> COLOR")
print("=" * 90)

response = requests.get(url, timeout=30)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "sld": "http://www.opengis.net/sld",
    "ogc": "http://www.opengis.net/ogc"
}

for rule in root.findall(".//sld:Rule", ns):

    name = rule.findtext(
        "sld:Name",
        default="",
        namespaces=ns
    )

    title = rule.findtext(
        "sld:Title",
        default="",
        namespaces=ns
    )

    codes = sorted(set(
        x.text.strip()
        for x in rule.findall(".//ogc:Literal", ns)
        if x.text and x.text.strip().isalpha()
    ))

    colors = sorted(set(
        x.text.strip()
        for x in rule.findall(".//sld:CssParameter", ns)
        if x.text and x.text.strip().startswith("#")
    ))

    if title and codes:
        print(
            f"{name:6} | "
            f"{title.replace(chr(10), ' ').strip():45} | "
            f"{','.join(codes):25} | "
            f"{','.join(colors)}"
        )

print("\nDONE")