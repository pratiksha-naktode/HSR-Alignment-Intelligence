from pathlib import Path
import re

xml = Path(r"data\processed\bhuvan_wms_capabilities.xml").read_text(
    errors="ignore"
)

# Find the main LULC layer block
match = re.search(
    r"<Layer[^>]*>.*?<Name>sisdp_lulc_v2</Name>.*?</Layer>",
    xml,
    re.IGNORECASE | re.DOTALL
)

if not match:
    print("sisdp_lulc_v2 layer block not found")
    raise SystemExit

block = match.group(0)

print("=" * 70)
print("SISDP LULC V2 LAYER")
print("=" * 70)

print("\nLayer name:")
print("sisdp_lulc_v2")

print("\nStyles found:")

styles = re.findall(
    r"<Style[^>]*>.*?<Name>(.*?)</Name>.*?</Style>",
    block,
    re.IGNORECASE | re.DOTALL
)

for style in styles:
    print("-", style.strip())

print("\nLegend URLs:")

urls = re.findall(
    r'xlink:href="([^"]*GetLegendGraphic[^"]*)"',
    block,
    re.IGNORECASE
)

for url in urls:
    print(url.replace("&amp;", "&"))

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)