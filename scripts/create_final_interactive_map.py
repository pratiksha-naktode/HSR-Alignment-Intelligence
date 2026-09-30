import geopandas as gpd
import pandas as pd
import folium
import json
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

DATA = BASE / "data" / "processed"
RESULTS = BASE / "data" / "results"

HIGHWAY_FILE = DATA / "highways_route_area.geojsonl"

OUTPUT = RESULTS / "hsr_routes_highway_interactions.html"


# ============================================================
# SETTINGS
# ============================================================

UTM_CRS = "EPSG:32643"
WEB_CRS = "EPSG:4326"

OVERLAP_THRESHOLD_M = 20


# ============================================================
# ROUTE COLORS
# ============================================================

ROUTE_COLORS = {
    "Route 1": "red",
    "Route 2": "green",
    "Route 3": "purple"
}


# ============================================================
# LOAD ROUTES AND CORRIDORS
# ============================================================

routes = {}
corridors = {}

for i in range(1, 4):

    route_name = f"Route {i}"

    centerline_file = DATA / f"Route_{i}_centerline.gpkg"
    corridor_file = DATA / f"Route_{i}_corridor_3_5m.gpkg"

    route = gpd.read_file(centerline_file)
    corridor = gpd.read_file(corridor_file)

    route = route.to_crs(WEB_CRS)
    corridor = corridor.to_crs(UTM_CRS)

    routes[route_name] = route
    corridors[route_name] = corridor

    print(
        f"{route_name}: "
        f"{len(route)} centerline feature(s), "
        f"{len(corridor)} corridor feature(s)"
    )


# ============================================================
# LOAD HIGHWAYS
# ============================================================

print()
print("Loading highway dataset...")

highways = gpd.read_file(HIGHWAY_FILE)

print(
    f"Highway features loaded: {len(highways)}"
)

print(
    f"Highway CRS: {highways.crs}"
)

highways = highways.to_crs(UTM_CRS)


# ============================================================
# HELPER FUNCTION
# ============================================================

def safe_value(row, column, default="Unknown"):

    if column in row.index:

        value = row[column]

        if pd.notna(value):

            text = str(value).strip()

            if text:
                return text

    return default


# ============================================================
# CALCULATE HIGHWAY INTERACTIONS
# ============================================================

interaction_records = []


for route_name, corridor in corridors.items():

    print()
    print("=" * 70)
    print(f"Processing {route_name}")
    print("=" * 70)

    # Merge corridor geometry
    corridor_geometry = corridor.geometry.union_all()

    # Spatial index candidate search
    candidate_index = list(
        highways.sindex.query(
            corridor_geometry,
            predicate="intersects"
        )
    )

    print(
        f"Candidate highway features: "
        f"{len(candidate_index)}"
    )

    interaction_count = 0

    for idx in candidate_index:

        highway_row = highways.iloc[idx]

        highway_geometry = highway_row.geometry

        if highway_geometry is None:
            continue

        if highway_geometry.is_empty:
            continue

        # Actual geometric interaction
        interaction_geometry = (
            highway_geometry.intersection(
                corridor_geometry
            )
        )

        if interaction_geometry.is_empty:
            continue

        interaction_length_m = (
            interaction_geometry.length
        )

        if interaction_length_m <= 0:
            continue

        interaction_count += 1

        # ----------------------------------------------------
        # CLASSIFICATION
        # ----------------------------------------------------

        if interaction_length_m <= OVERLAP_THRESHOLD_M:
            interaction_type = "Short / Crossing-type"
        else:
            interaction_type = "Extended / Overlap-type"

        # ----------------------------------------------------
        # ATTRIBUTES
        # ----------------------------------------------------

        road_name = safe_value(
            highway_row,
            "road_name"
        )

        road_type = safe_value(
            highway_row,
            "road_type"
        )

        lane_status = safe_value(
            highway_row,
            "lane_statu"
        )

        status = safe_value(
            highway_row,
            "status"
        )

        category = safe_value(
            highway_row,
            "category"
        )

        # ----------------------------------------------------
        # SAVE RECORD
        # ----------------------------------------------------

        interaction_records.append({
            "route": route_name,
            "road_name": road_name,
            "road_type": road_type,
            "lane_status": lane_status,
            "status": status,
            "category": category,
            "interaction_length_m":
                interaction_length_m,
            "interaction_length_km":
                interaction_length_m / 1000,
            "interaction_type":
                interaction_type,
            "geometry":
                interaction_geometry
        })

    print(
        f"Actual interactions found: "
        f"{interaction_count}"
    )


# ============================================================
# CREATE INTERACTION GEODATAFRAME
# ============================================================

interactions = gpd.GeoDataFrame(
    interaction_records,
    geometry="geometry",
    crs=UTM_CRS
)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 70)
print("INTERACTION VALIDATION")
print("=" * 70)

print(
    f"Total interactions: {len(interactions)}"
)

for route_name in ROUTE_COLORS:

    route_data = interactions[
        interactions["route"] == route_name
    ]

    total_km = (
        route_data[
            "interaction_length_km"
        ].sum()
    )

    short_count = (
        route_data[
            "interaction_type"
        ]
        .eq("Short / Crossing-type")
        .sum()
    )

    extended_count = (
        route_data[
            "interaction_type"
        ]
        .eq("Extended / Overlap-type")
        .sum()
    )

    print()
    print(route_name)
    print(
        f"  Interactions: {len(route_data)}"
    )
    print(
        f"  Total length: {total_km:.4f} km"
    )
    print(
        f"  Short/Crossing: {short_count}"
    )
    print(
        f"  Extended/Overlap: {extended_count}"
    )


# ============================================================
# CONVERT TO WEB CRS
# ============================================================

interactions_web = interactions.to_crs(
    WEB_CRS
)


# ============================================================
# COMBINE ROUTES FOR MAP EXTENT
# ============================================================

all_routes = gpd.GeoDataFrame(
    pd.concat(
        routes.values(),
        ignore_index=True
    ),
    crs=WEB_CRS
)


# ============================================================
# MAP CENTER
# ============================================================

try:
    combined_geometry = (
        all_routes.geometry.union_all()
    )
except AttributeError:
    combined_geometry = (
        all_routes.geometry.unary_union
    )

centroid = combined_geometry.centroid

center_lat = centroid.y
center_lon = centroid.x

print()
print(
    f"Map center: "
    f"{center_lat:.6f}, "
    f"{center_lon:.6f}"
)


# ============================================================
# CREATE MAP
# ============================================================

m = folium.Map(
    location=[
        center_lat,
        center_lon
    ],
    zoom_start=7,
    tiles=None,
    control_scale=True
)


# ============================================================
# BASEMAP
# ============================================================

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/"
        "World_Street_Map/"
        "MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Street Map",
    name="Esri Street Map"
).add_to(m)


# ============================================================
# HSR ROUTES
# ============================================================

route_group = folium.FeatureGroup(
    name="HSR Routes",
    show=True
)


for route_name, route_gdf in routes.items():

    color = ROUTE_COLORS[route_name]

    folium.GeoJson(
        route_gdf.to_json(),

        name=route_name,

        tooltip=folium.Tooltip(
            route_name
        ),

        style_function=lambda feature,
        color=color: {
            "color": color,
            "weight": 5,
            "opacity": 0.9
        }

    ).add_to(route_group)


route_group.add_to(m)
# ============================================================
# ENVIRONMENTAL LULC IMPACT LAYERS
# ============================================================

print("Loading environmental LULC layers...")

LULC_FILES = {
    "Route 1": (
        DATA / "Route_1_lulc_intersections_final.gpkg",
        "lulc_intersections",
        "Level_I"
    ),
    "Route 2": (
        DATA / "Route_2_lulc_intersections_final.gpkg",
        "route2_lulc",
        "category"
    ),
    "Route 3": (
        DATA / "Route_3_lulc_intersections_final.gpkg",
        "route2_lulc",
        "category"
    ),
}

ENVIRONMENTAL_CATEGORIES = [
    "Forest",
    "Agriculture",
    "Built-up",
    "Water Bodies",
    "Wastelands",
    "Others"
]

environmental_groups = {}

for category in ENVIRONMENTAL_CATEGORIES:

    environmental_groups[category] = folium.FeatureGroup(
        name=f"{category} Impact",
        show=False
    )

for route_name, (file_path, layer_name, category_column) in LULC_FILES.items():

    lulc = gpd.read_file(
        file_path,
        layer=layer_name
    )

    lulc = lulc.to_crs(WEB_CRS)

    lulc["route"] = route_name
    lulc["map_category"] = (
        lulc[category_column]
        .fillna("Others")
        .astype(str)
    )

    for category in ENVIRONMENTAL_CATEGORIES:

        category_data = lulc[
            lulc["map_category"] == category
        ].copy()

        if category_data.empty:
            continue

        folium.GeoJson(
            category_data.to_json(),

            tooltip=folium.GeoJsonTooltip(
                fields=[
                    "route",
                    "map_category",
                    "impact_area_km2"
                ],
                aliases=[
                    "Route",
                    "Land-use Category",
                    "Impact Area (km²)"
                ],
                localize=True
            ),

            style_function=lambda feature: {
                "fillOpacity": 0.35,
                "weight": 0.8
            }

        ).add_to(
            environmental_groups[category]
        )

for group in environmental_groups.values():
    group.add_to(m)

print("Environmental LULC layers added:")
for category in ENVIRONMENTAL_CATEGORIES:
    print(f" - {category}")




# ============================================================
# STATION CANDIDATES
# ============================================================

print()
print("Loading station GIS layer...")

STATION_FILE = DATA / "station_screening.gpkg"

stations = gpd.read_file(
    STATION_FILE,
    layer="station_screening"
)

stations = stations.to_crs(WEB_CRS)

print(
    f"Station candidates loaded: {len(stations)}"
)


station_group = folium.FeatureGroup(
    name="Station Candidates",
    show=True
)


station_group.add_to(m)
# ============================================================
# STATION INFORMATION PANEL
# ============================================================

station_records = []

for _, row in stations.iterrows():

    station_id = safe_value(row, "station_id")
    route = safe_value(row, "route")
    station_type = safe_value(row, "station_type")

    chainage = (
        f"{row['chainage_km']:.3f} km"
        if pd.notna(row["chainage_km"])
        else "Unknown"
    )

    access = safe_value(
        row,
        "access_summary",
        "Unknown"
    )

    education_count = safe_value(
        row,
        "education_1km",
        "0"
    )

    schools = safe_value(
        row,
        "schools_1km",
        "0"
    )

    colleges = safe_value(
        row,
        "colleges_1km",
        "0"
    )

    universities = safe_value(
        row,
        "universities_1km",
        "0"
    )

    highway_500m = safe_value(
        row,
        "highways_500m",
        "0"
    )

    highway_1km = safe_value(
        row,
        "highways_1km",
        "0"
    )

    highway_5km = safe_value(
        row,
        "highways_5km",
        "0"
    )

    nearest_education = safe_value(
        row,
        "nearest_education",
        "None"
    )

    nearest_highway = safe_value(
        row,
        "nearest_highway",
        "None"
    )

    highway_proximity = safe_value(
        row,
        "highway_proximity_class",
        "Unknown"
    )


    # --------------------------------------------------------
    # Marker appearance based on factual screening category
    # --------------------------------------------------------

    marker_colors = {
        "Education + Highway": "blue",
        "Education Only": "green",
        "Highway Only": "orange",
        "Limited Nearby Access": "gray"
    }

    marker_color = marker_colors.get(
        access,
        "gray"
    )


    # --------------------------------------------------------
    # Popup
    # --------------------------------------------------------

    popup_html = f"""
    <div style="font-size:13px; width:330px">

        <h4>HSR Station Candidate</h4>

        <b>Station ID:</b>
        {station_id}<br>

        <b>Route:</b>
        {route}<br>

        <b>Type:</b>
        {station_type}<br>

        <b>Chainage:</b>
        {chainage}<br>

        <b>Distance from End:</b>
        {row["distance_end_km"]:.3f} km<br>

        <hr>

        <b>Access Screening:</b><br>
        {access}<br>

        <hr>

        <b>Education within 1 km:</b>
        {education_count}<br>

        <b>Schools:</b>
        {schools}<br>

        <b>Colleges:</b>
        {colleges}<br>

        <b>Universities:</b>
        {universities}<br>

        <b>Nearest Education:</b>
        {nearest_education}<br>
        <b>Distance:</b>
        {row["nearest_education_km"]:.3f} km<br>

        <hr>

        <b>Highways within 500 m:</b>
        {highway_500m}<br>

        <b>Highways within 1 km:</b>
        {highway_1km}<br>

        <b>Highways within 5 km:</b>
        {highway_5km}<br>

        <b>Nearest Highway:</b>
        {nearest_highway}<br>
        <b>Distance:</b>
        {row["nearest_highway_km"]:.3f} km<br>

        <b>Highway Proximity:</b>
        {highway_proximity}

    </div>
    """


    # --------------------------------------------------------
    # Store station data for the interactive search panel
    # --------------------------------------------------------

    station_records.append({
        "station_id": station_id,
        "route": route,
        "station_type": station_type,
        "chainage_km": float(row["chainage_km"]) if pd.notna(row["chainage_km"]) else None,
        "distance_end_km": float(row["distance_end_km"]) if pd.notna(row["distance_end_km"]) else None,
        "latitude": float(row["latitude"]) if pd.notna(row["latitude"]) else None,
        "longitude": float(row["longitude"]) if pd.notna(row["longitude"]) else None,
        "education_1km": education_count,
        "schools_1km": schools,
        "colleges_1km": colleges,
        "universities_1km": universities,
        "nearest_education": nearest_education,
        "nearest_education_km": float(row["nearest_education_km"]) if pd.notna(row["nearest_education_km"]) else None,
        "highways_500m": highway_500m,
        "highways_1km": highway_1km,
        "highways_5km": highway_5km,
        "nearest_highway": nearest_highway,
        "nearest_highway_km": float(row["nearest_highway_km"]) if pd.notna(row["nearest_highway_km"]) else None,
        "nearest_highway_type": nearest_highway_type if "nearest_highway_type" in locals() else safe_value(row, "nearest_highway_type", "Unknown"),
        "nearest_highway_state": nearest_highway_state if "nearest_highway_state" in locals() else safe_value(row, "nearest_highway_state", "Unknown"),
        "access_summary": access,
        "highway_proximity_class": highway_proximity
    })

    folium.CircleMarker(
        location=[
            row.geometry.y,
            row.geometry.x
        ],

        radius=6,

        tooltip=(
            f"{station_id} | "
            f"{route} | "
            f"{chainage}"
        ),

        popup=folium.Popup(
            popup_html,
            max_width=400
        ),

        color=marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.85
    ).add_to(station_group)

station_json = json.dumps(
    station_records
)


station_panel = f"""
<style>

#station-panel {{
    position: fixed;
    top: 80px;
    right: 360px;
    z-index: 9999;
    background: white;
    padding: 12px;
    width: 300px;
    max-height: 400px;
    overflow-y: auto;
    border: 2px solid #555;
    border-radius: 6px;
    font-family: Arial;
    font-size: 13px;
}}

#station-panel h4 {{
    margin-top: 0;
}}

#station-route {{
    width: 100%;
    padding: 5px;
    margin-bottom: 8px;
}}

#station-chainage {{
    width: 100%;
}}

</style>

<div id="station-panel">

<h4>Station Candidate Search</h4>

<select id="station-route">
    <option value="Route 1">Route 1</option>
    <option value="Route 2">Route 2</option>
    <option value="Route 3">Route 3</option>
</select>

<br><br>

<label>
Chainage (km):
</label>

<input
    id="station-chainage"
    type="number"
    min="0"
    step="5"
    value="0"
/>

<br><br>

<button onclick="findNearestStation()">
Find Candidate
</button>

<div id="station-result"
     style="margin-top:10px;">
</div>

</div>

<script>

var stationData = {station_json};

function findNearestStation() {{

    var route =
        document.getElementById(
            "station-route"
        ).value;

    var chainage =
        parseFloat(
            document.getElementById(
                "station-chainage"
            ).value
        );

    var candidates =
        stationData.filter(
            function(station) {{
                return station.route === route;
            }}
        );

    if (candidates.length === 0) {{

        document.getElementById(
            "station-result"
        ).innerHTML =
            "No candidates found.";

        return;
    }}

    var nearest =
        candidates.reduce(
            function(previous, current) {{

                return Math.abs(
                    current.chainage_km -
                    chainage
                )
                <
                Math.abs(
                    previous.chainage_km -
                    chainage
                )
                ? current
                : previous;

            }}
        );

    document.getElementById(
        "station-result"
    ).innerHTML =

        "<b>Station:</b> "
        + nearest.station_id
        + "<br>"

        + "<b>Route:</b> "
        + nearest.route
        + "<br>"

        + "<b>Chainage:</b> "
        + nearest.chainage_km
        + " km<br>"

        + "<b>Distance from End:</b> "
        + nearest.distance_end_km
        + " km<br><br>"

        + "<b>Education within 1 km:</b> "
        + nearest.education_1km
        + "<br>"

        + "<b>Highways within 500 m:</b> "
        + nearest.highways_500m
        + "<br>"

        + "<b>Highways within 1 km:</b> "
        + nearest.highways_1km
        + "<br>"

        + "<b>Highways within 5 km:</b> "
        + nearest.highways_5km
        + "<br><br>"

        + "<b>Nearest Education:</b> "
        + nearest.nearest_education
        + " (" + nearest.nearest_education_km + " km)<br>"

        + "<b>Nearest Highway:</b> "
        + nearest.nearest_highway
        + " (" + nearest.nearest_highway_km + " km)<br>"

        + "<b>Access:</b> "
        + nearest.access_summary;

}}

</script>
"""


m.get_root().html.add_child(
    folium.Element(
        station_panel
    )
)

print(
    "Station candidate layer added to map."
)

# ============================================================
# SHORT / CROSSING INTERACTIONS
# ============================================================

short_group = folium.FeatureGroup(
    name="Highway Interactions - Short/Crossing",
    show=True
)


short_data = interactions_web[
    interactions_web[
        "interaction_type"
    ] == "Short / Crossing-type"
]


for _, row in short_data.iterrows():

    popup_html = f"""
    <div style="font-size:13px">

    <b>HSR Route:</b>
    {row['route']}<br><br>

    <b>Road Name:</b>
    {row['road_name']}<br>

    <b>Road Type:</b>
    {row['road_type']}<br>

    <b>Lane Status:</b>
    {row['lane_status']}<br>

    <b>Status:</b>
    {row['status']}<br>

    <b>Category:</b>
    {row['category']}<br>

    <b>Interaction Length:</b>
    {row['interaction_length_m']:.2f} m<br>

    <b>Interaction Type:</b>
    Short / Crossing-type

    </div>
    """

    folium.GeoJson(
        row.geometry.__geo_interface__,

        tooltip=(
            f"{row['route']} | "
            f"{row['road_name']} | "
            f"{row['interaction_length_m']:.1f} m"
        ),

        popup=folium.Popup(
            popup_html,
            max_width=350
        ),

        style_function=lambda feature: {
            "color": "blue",
            "weight": 4,
            "opacity": 0.9
        }

    ).add_to(short_group)


short_group.add_to(m)


# ============================================================
# EXTENDED / OVERLAP INTERACTIONS
# ============================================================

extended_group = folium.FeatureGroup(
    name="Highway Interactions - Extended/Overlap",
    show=True
)


extended_data = interactions_web[
    interactions_web[
        "interaction_type"
    ] == "Extended / Overlap-type"
]


for _, row in extended_data.iterrows():

    popup_html = f"""
    <div style="font-size:13px">

    <b>HSR Route:</b>
    {row['route']}<br><br>

    <b>Road Name:</b>
    {row['road_name']}<br>

    <b>Road Type:</b>
    {row['road_type']}<br>

    <b>Lane Status:</b>
    {row['lane_status']}<br>

    <b>Status:</b>
    {row['status']}<br>

    <b>Category:</b>
    {row['category']}<br>

    <b>Interaction Length:</b>
    {row['interaction_length_m']:.2f} m<br>

    <b>Interaction Length:</b>
    {row['interaction_length_km']:.4f} km<br>

    <b>Interaction Type:</b>
    Extended / Overlap-type

    </div>
    """

    folium.GeoJson(
        row.geometry.__geo_interface__,

        tooltip=(
            f"{row['route']} | "
            f"{row['road_name']} | "
            f"{row['interaction_length_m']:.1f} m"
        ),

        popup=folium.Popup(
            popup_html,
            max_width=350
        ),

        style_function=lambda feature: {
            "color": "orange",
            "weight": 5,
            "opacity": 0.95
        }

    ).add_to(extended_group)


extended_group.add_to(m)


# ============================================================
# FIT MAP TO ROUTES
# ============================================================

minx, miny, maxx, maxy = (
    all_routes.total_bounds
)

m.fit_bounds(
    [
        [miny, minx],
        [maxy, maxx]
    ]
)

# ============================================================
# ROUTE SUMMARY PANEL
# ============================================================

route_summary = {
    "Route 1": {
        "length": 788.78495,
        "forest_area": 0.048307,
        "forest_length": 13.815291,
        "agri_area": 0.878612,
        "agri_length": 250.905164,
        "builtup_area": 0.781871,
        "builtup_length": 223.739566,
        "wetland_area": 0.024743,
        "wetland_length": 7.069507,
        "waterbody_area": 0.004953,
        "waterbody_length": 1.476821,
        "education": 39,
        "highways": 60,
        "esz": 1.459039,
        "water_distance": 0.0069,
        "topsis": 0.612012
    },

    "Route 2": {
        "length": 789.90222,
        "forest_area": 0.055493,
        "forest_length": 15.927911,
        "agri_area": 1.571022,
        "agri_length": 449.120527,
        "builtup_area": 0.736322,
        "builtup_length": 210.884850,
        "wetland_area": 0.063228,
        "wetland_length": 18.071516,
        "waterbody_area": 0.026979,
        "waterbody_length": 7.428458,
        "education": 31,
        "highways": 55,
        "esz": 3.398557,
        "water_distance": 0.0037,
        "topsis": 0.419965
    },

    "Route 3": {
        "length": 799.26005,
        "forest_area": 0.056215,
        "forest_length": 16.029821,
        "agri_area": 1.532198,
        "agri_length": 437.911220,
        "builtup_area": 0.793088,
        "builtup_length": 226.904203,
        "wetland_area": 0.044774,
        "wetland_length": 12.786078,
        "waterbody_area": 0.020807,
        "waterbody_length": 6.001669,
        "education": 39,
        "highways": 55,
        "esz": 3.653662,
        "water_distance": 0.1885,
        "topsis": 0.420054
    }
}

summary_html = """
<div style="
position: fixed;
top: 10px;
right: 10px;
z-index: 9999;
background: white;
padding: 12px;
border: 2px solid #444;
border-radius: 8px;
width: 330px;
max-height: 85vh;
overflow-y: auto;
font-family: Arial;
font-size: 13px;
">

<h3 style="margin-top:0;">HSR Route Summary</h3>

<label><b>Select Route:</b></label>

<select id="routeSummarySelect"
        onchange="updateRouteSummary()"
        style="width:100%; padding:5px; margin:6px 0 10px 0;">

<option value="Route 1">Route 1</option>
<option value="Route 2">Route 2</option>
<option value="Route 3">Route 3</option>

</select>

<div id="routeSummaryContent"></div>

</div>

<script>

const routeSummaryData = """ + json.dumps(route_summary) + """;

function updateRouteSummary() {

    const route = document.getElementById("routeSummarySelect").value;
    const d = routeSummaryData[route];

    document.getElementById("routeSummaryContent").innerHTML = `

    <h4>${route}</h4>

    <b>Route Length</b><br>
    ${d.length.toFixed(3)} km

    <hr>

    <b>Environmental Impact</b>

    <table style="width:100%; font-size:12px;">
    <tr>
        <td>Forest</td>
        <td>${d.forest_area.toFixed(6)} km²</td>
        <td>${d.forest_length.toFixed(3)} km</td>
    </tr>

    <tr>
        <td>Agriculture</td>
        <td>${d.agri_area.toFixed(6)} km²</td>
        <td>${d.agri_length.toFixed(3)} km</td>
    </tr>

    <tr>
        <td>Built-up</td>
        <td>${d.builtup_area.toFixed(6)} km²</td>
        <td>${d.builtup_length.toFixed(3)} km</td>
    </tr>

    <tr>
        <td>Wetland</td>
        <td>${d.wetland_area.toFixed(6)} km²</td>
        <td>${d.wetland_length.toFixed(3)} km</td>
    </tr>

    <tr>
        <td>Water Bodies</td>
        <td>${d.waterbody_area.toFixed(6)} km²</td>
        <td>${d.waterbody_length.toFixed(3)} km</td>
    </tr>
    </table>

    <hr>

    <b>Social / Infrastructure</b>

    <br>Education within 100 m:
    <b>${d.education}</b>

    <br>Highway Intersections:
    <b>${d.highways}</b>

    <hr>

    <b>Proximity</b>

    <br>Nearest ESZ:
    <b>${d.esz.toFixed(3)} km</b>

    <br>Nearest Waterbody:
    <b>${d.water_distance.toFixed(4)} km</b>

    <hr>

    <b>TOPSIS Score:</b>
    ${d.topsis.toFixed(6)}

    `;
}

updateRouteSummary();

</script>
"""

m.get_root().html.add_child(folium.Element(summary_html))

# ============================================================
# AHP + TOPSIS + SENSITIVITY PANEL
# ============================================================

mcdm_html = """
<div id="mcdm-panel"
     style="
     position: fixed;
     bottom: 10px;
     right: 10px;
     z-index: 9999;
     background: white;
     padding: 12px;
     width: 360px;
     max-height: 430px;
     overflow-y: auto;
     border: 2px solid #444;
     border-radius: 8px;
     font-family: Arial;
     font-size: 12px;
     box-shadow: 0 2px 8px rgba(0,0,0,0.25);
     ">

<h3 style="margin-top:0;">AHP &amp; TOPSIS Decision Analysis</h3>

<b>AHP Criteria Weights</b>

<table style="width:100%; border-collapse:collapse; margin-top:6px;">
<tr><th style="text-align:left;">Criterion</th><th>Weight</th></tr>
<tr><td>Forest</td><td>16.94%</td></tr>
<tr><td>Agriculture</td><td>10.20%</td></tr>
<tr><td>Built-up</td><td>9.44%</td></tr>
<tr><td>Education</td><td>5.87%</td></tr>
<tr><td>Wetland</td><td>20.02%</td></tr>
<tr><td>Waterbody</td><td>6.63%</td></tr>
<tr><td>ESZ</td><td>14.99%</td></tr>
<tr><td>Route Length</td><td>8.74%</td></tr>
<tr><td>Highway</td><td>7.16%</td></tr>
</table>

<p style="margin-bottom:8px;">
<b>Consistency Ratio:</b> 0.0133
</p>

<hr>

<b>TOPSIS Results</b>

<table style="width:100%; border-collapse:collapse; margin-top:6px;">
<tr><th>Route</th><th>Score</th><th>Rank</th></tr>
<tr><td>Route 1</td><td>0.612012</td><td>1</td></tr>
<tr><td>Route 2</td><td>0.419965</td><td>3</td></tr>
<tr><td>Route 3</td><td>0.420054</td><td>2</td></tr>
</table>

<hr>

<b>Sensitivity Analysis</b>

<p style="margin:6px 0;">
Across the eight tested weighting scenarios, Route 1 remained in position 1.
Routes 2 and 3 changed relative position depending on the weighting scenario.
</p>

<table style="width:100%; border-collapse:collapse; margin-top:6px;">
<tr><th>Scenario</th><th>R1</th><th>R2</th><th>R3</th></tr>
<tr><td>Baseline AHP</td><td>0.612012</td><td>0.419965</td><td>0.420054</td></tr>
<tr><td>Equal Weights</td><td>0.540434</td><td>0.521867</td><td>0.390529</td></tr>
<tr><td>Environmental Focus</td><td>0.623205</td><td>0.387451</td><td>0.444094</td></tr>
<tr><td>Agriculture Focus</td><td>0.627658</td><td>0.401517</td><td>0.401890</td></tr>
<tr><td>Social Development</td><td>0.579886</td><td>0.459028</td><td>0.396266</td></tr>
<tr><td>Infrastructure Focus</td><td>0.604688</td><td>0.455733</td><td>0.424041</td></tr>
<tr><td>Water Environment</td><td>0.666638</td><td>0.356767</td><td>0.428961</td></tr>
<tr><td>Forest Focus</td><td>0.687211</td><td>0.346309</td><td>0.327491</td></tr>
</table>

<p style="font-size:11px; margin-bottom:0;">
TOPSIS uses the nine defined decision criteria. The five environmental
intersection-length metrics are supplementary reporting metrics and are
not additional TOPSIS criteria.
</p>

</div>
"""

m.get_root().html.add_child(
    folium.Element(mcdm_html)
)

# ============================================================
# LAYER CONTROL
# ============================================================

folium.LayerControl(
    collapsed=False
).add_to(m)


# ============================================================
# SAVE MAP
# ============================================================

m.save(OUTPUT)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 80)
print("HSR HIGHWAY INTERACTION MAP CREATED SUCCESSFULLY")
print("=" * 80)

print()
print("Output:")
print(OUTPUT)

print()
print("Map layers:")
print(" - HSR Routes")
print(" - Highway Interactions - Short/Crossing")
print(" - Highway Interactions - Extended/Overlap")