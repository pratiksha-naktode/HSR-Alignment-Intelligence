import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from pathlib import Path
import xml.etree.ElementTree as ET

PROJECT = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
PROCESSED = PROJECT / "data" / "processed"

# Read Bhuvan layer metadata
xml_path = PROCESSED / "bhuvan_wms_capabilities.xml"
ns = {"wms": "http://www.opengis.net/wms"}
root = ET.parse(xml_path).getroot()

records = []

for layer in root.findall(".//wms:Layer", ns):
    name = layer.findtext("wms:Name", namespaces=ns)

    if not name or "_lulc_v2" not in name:
        continue

    bbox = layer.find("wms:EX_GeographicBoundingBox", ns)

    if bbox is None:
        continue

    west = float(bbox.findtext("wms:westBoundLongitude", namespaces=ns))
    south = float(bbox.findtext("wms:southBoundLatitude", namespaces=ns))
    east = float(bbox.findtext("wms:eastBoundLongitude", namespaces=ns))
    north = float(bbox.findtext("wms:northBoundLatitude", namespaces=ns))

    records.append({
        "layer": name,
        "geometry": box(west, south, east, north)
    })

districts = gpd.GeoDataFrame(records, crs="EPSG:4326")

# Check each route
for i in range(1, 4):
    route_path = PROCESSED / f"Route_{i}_centerline.gpkg"

    route = gpd.read_file(route_path).to_crs("EPSG:4326")

    candidates = districts[districts.geometry.intersects(route.unary_union)]

    print(f"\nRoute {i}")
    print("Candidate LULC districts:", len(candidates))

    for name in candidates["layer"]:
        print("  ", name)
