import re

p = r"data\processed\bhuvan_wms_capabilities.xml"
s = open(p, encoding="utf-8").read()

pattern = r"<Layer>.*?</Layer>"

layers = re.findall(pattern, s, flags=re.DOTALL)

for layer in layers:
    if "MH" in layer.upper() or "MAHARASHTRA" in layer.upper():
        name = re.search(r"<Name>(.*?)</Name>", layer)
        title = re.search(r"<Title>(.*?)</Title>", layer)

        if name or title:
            print(
                "NAME:", name.group(1) if name else "",
                "| TITLE:", title.group(1) if title else ""
            )