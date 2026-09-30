import geopandas as gpd
import folium
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

CORRIDOR = (
    BASE
    / "data"
    / "processed"
    / "Route_1_corridor_2m.gpkg"
)

HIGHWAYS = (
    BASE
    / "data"
    / "processed"
    / "highways_route_area.geojsonl"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "route1_highway_interactive.html"
)

# --------------------------------------------------
# 1. Load GIS data
# --------------------------------------------------

corridor = gpd.read_file(CORRIDOR)
highways = gpd.read_file(HIGHWAYS)

print("Corridor loaded:", len(corridor))
print("Highways loaded:", len(highways))

# --------------------------------------------------
# 2. Convert to metric CRS
# --------------------------------------------------

corridor_metric = corridor.to_crs("EPSG:32643")
highways_metric = highways.to_crs("EPSG:32643")

route_geometry = corridor_metric.geometry.iloc[0]

# --------------------------------------------------
# 3. Find highway intersections
# --------------------------------------------------

intersections = highways_metric[
    highways_metric.geometry.intersects(route_geometry)
].copy()

intersections["intersection_length_m"] = (
    intersections.geometry
    .intersection(route_geometry)
    .length
)

print("Intersecting highway records:", len(intersections))

# --------------------------------------------------
# 4. Keep large intersections
# --------------------------------------------------

large = intersections[
    intersections["intersection_length_m"] >= 300
].copy()

print("Large intersections >= 300 m:", len(large))

# --------------------------------------------------
# 5. Convert to WGS84 for web map
# --------------------------------------------------

corridor_wgs = corridor_metric.to_crs("EPSG:4326")
large_wgs = large.to_crs("EPSG:4326")

# --------------------------------------------------
# 6. Find map center
# --------------------------------------------------

centroid = corridor_wgs.geometry.iloc[0].centroid

m = folium.Map(
    location=[centroid.y, centroid.x],
    zoom_start=9,
    tiles=None
)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Esri World Street Map"
).add_to(m)
# --------------------------------------------------
# 7. Add HSR corridor
# --------------------------------------------------

folium.GeoJson(
    corridor_wgs,
    name="HSR Route 1 Corridor",
    style_function=lambda feature: {
        "color": "red",
        "weight": 5,
        "opacity": 0.9
    },
    tooltip="HSR Route 1 Corridor"
).add_to(m)

# --------------------------------------------------
# 8. Add large highway intersections
# --------------------------------------------------

for _, row in large_wgs.iterrows():

    road_name = row.get("road_name")
    road_class = row.get("road_class")
    lane = row.get("lane_status_clean")
    status = row.get("status")
    length = row.get("intersection_length_m")

    # Handle missing values
    if str(road_name) == "nan":
        road_name = "Unknown"

    if str(lane) == "nan":
        lane = "Unknown"

    if str(status) == "nan":
        status = "Unknown"

    popup_text = f"""
    <b>Road:</b> {road_name}<br>
    <b>Road Class:</b> {road_class}<br>
    <b>Lanes:</b> {lane}<br>
    <b>Status:</b> {status}<br>
    <b>Intersection Length:</b> {length:.2f} m
    """

    folium.GeoJson(
        row.geometry,
        style_function=lambda feature: {
            "color": "blue",
            "weight": 6,
            "opacity": 0.9
        },
        tooltip=f"{road_name} — {length:.1f} m",
        popup=folium.Popup(
            popup_text,
            max_width=350
        )
    ).add_to(m)

# --------------------------------------------------
# 9. Add layer control
# --------------------------------------------------

folium.LayerControl().add_to(m)

# --------------------------------------------------
# 10. Save interactive map
# --------------------------------------------------

m.save(OUTPUT)

print()
print("==============================================")
print("INTERACTIVE MAP CREATED")
print("==============================================")
print("Large intersections:", len(large))
print("Saved to:")
print(OUTPUT)