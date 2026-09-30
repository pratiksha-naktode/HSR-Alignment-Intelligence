import re
from pathlib import Path

xml_file = Path(r"data\processed\bhuvan_wms_capabilities.xml")
text = xml_file.read_text(errors="ignore")

layers = sorted(set(re.findall(r"<Name>([^<]*lulc[^<]*)</Name>", text, re.I)))

print("=" * 70)
print("LULC LAYERS FOUND")
print("=" * 70)

for layer in layers:
    print(layer)

print("\nTotal LULC layers:", len(layers))