import xml.etree.ElementTree as ET

path = r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed\bhuvan_wms_capabilities.xml"

ns = {"wms": "http://www.opengis.net/wms"}

root = ET.parse(path).getroot()

layers = []

for layer in root.findall(".//wms:Layer", ns):
    name = layer.findtext("wms:Name", namespaces=ns)

    if name and "_lulc_v2" in name:
        bbox = layer.find("wms:EX_GeographicBoundingBox", ns)

        if bbox is not None:
            west = bbox.findtext("wms:westBoundLongitude", namespaces=ns)
            south = bbox.findtext("wms:southBoundLatitude", namespaces=ns)
            east = bbox.findtext("wms:eastBoundLongitude", namespaces=ns)
            north = bbox.findtext("wms:northBoundLatitude", namespaces=ns)

            layers.append((name, west, south, east, north))

print("LULC layers with bounding boxes:", len(layers))

for item in layers[:20]:
    print(item)
