import re
from pathlib import Path

xml_file = Path(r"data\processed\bhuvan_wms_capabilities.xml")

text = xml_file.read_text(errors="ignore")

keywords = [
    "SISDP_P2_LULC",
    "LULC_10K",
    "Forest",
    "Agriculture",
    "Built",
    "Urban",
]

print("=" * 70)
print("BHUVAN LULC SERVICE CHECK")
print("=" * 70)

for keyword in keywords:
    matches = list(re.finditer(keyword, text, re.IGNORECASE))

    print(f"\n{keyword}: {len(matches)} matches")

    for m in matches[:5]:
        start = max(0, m.start() - 250)
        end = min(len(text), m.end() + 500)

        print("-" * 60)
        print(text[start:end].replace("\n", " ")[:750])

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)