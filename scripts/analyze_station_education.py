import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# STATION CANDIDATE - EDUCATION ANALYSIS
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"
RESULTS = BASE / "data" / "results"

EDUCATION_FILE = (
    Path(
        r"C:\Users\Texaxs\Downloads\ROUTE_OPT"
    )
    / "ctiteria_dataset"
    / "hotosm_ind_education_facilities_polygons_geojson.geojson"
)

STATION_FILE = (
    PROCESSED /
    "station_candidates_final.gpkg"
)

OUTPUT_FILE = (
    PROCESSED /
    "station_education.gpkg"
)

CSV_FILE = (
    RESULTS /
    "station_education.csv"
)


# ============================================================
# SETTINGS
# ============================================================

# Station education screening radius
EDUCATION_RADIUS_M = 1000


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("STATION CANDIDATE - EDUCATION ANALYSIS")
print("=" * 80)

stations = gpd.read_file(
    STATION_FILE,
    layer="station_candidates"
)

education = gpd.read_file(
    EDUCATION_FILE
)

print(
    f"Station candidates: {len(stations)}"
)

print(
    f"Education features: {len(education)}"
)


# ============================================================
# VALIDATE DATA
# ============================================================

required_station_columns = [
    "candidate_id",
    "route",
    "chainage_km",
    "geometry",
]

required_education_columns = [
    "name",
    "name:en",
    "amenity",
    "geometry",
]

for column in required_station_columns:

    if column not in stations.columns:

        raise ValueError(
            f"Missing station column: {column}"
        )


for column in required_education_columns:

    if column not in education.columns:

        raise ValueError(
            f"Missing education column: {column}"
        )


# ============================================================
# PROJECT TO METRIC CRS
# ============================================================

stations_metric = stations.to_crs(
    "EPSG:32643"
)

education_metric = education.to_crs(
    "EPSG:32643"
)


# ============================================================
# BUILD SPATIAL INDEX
# ============================================================

education_sindex = education_metric.sindex


# ============================================================
# ANALYZE EACH STATION CANDIDATE
# ============================================================

results = []


for _, station in stations_metric.iterrows():

    candidate_id = station[
        "candidate_id"
    ]

    route = station[
        "route"
    ]

    chainage = station[
        "chainage_km"
    ]

    point = station.geometry


    # --------------------------------------------------------
    # Search within 1 km
    # --------------------------------------------------------

    search_area = point.buffer(
        EDUCATION_RADIUS_M
    )

    possible_indices = list(
        education_sindex.intersection(
            search_area.bounds
        )
    )


    if not possible_indices:

        results.append({

            "candidate_id":
                candidate_id,

            "route":
                route,

            "chainage_km":
                chainage,

            "education_within_1km":
                0,

            "schools_within_1km":
                0,

            "colleges_within_1km":
                0,

            "universities_within_1km":
                0,

            "nearest_education_distance_m":
                None,

            "nearest_education_distance_km":
                None,

            "nearest_education_name":
                None,

            "nearest_education_type":
                None,

        })

        continue


    nearby = education_metric.iloc[
        possible_indices
    ].copy()


    # --------------------------------------------------------
    # Exact distance
    # --------------------------------------------------------

    nearby[
        "distance_m"
    ] = nearby.geometry.distance(
        point
    )


    # Only features within 1 km
    nearby = nearby[
        nearby[
            "distance_m"
        ] <= EDUCATION_RADIUS_M
    ].copy()


    if nearby.empty:

        results.append({

            "candidate_id":
                candidate_id,

            "route":
                route,

            "chainage_km":
                chainage,

            "education_within_1km":
                0,

            "schools_within_1km":
                0,

            "colleges_within_1km":
                0,

            "universities_within_1km":
                0,

            "nearest_education_distance_m":
                None,

            "nearest_education_distance_km":
                None,

            "nearest_education_name":
                None,

            "nearest_education_type":
                None,

        })

        continue


    # --------------------------------------------------------
    # Normalize amenity type
    # --------------------------------------------------------

    nearby[
        "_amenity"
    ] = (
        nearby[
            "amenity"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )


    # --------------------------------------------------------
    # Count education categories
    # --------------------------------------------------------

    schools = nearby[
        nearby["_amenity"] == "school"
    ]

    colleges = nearby[
        nearby["_amenity"] == "college"
    ]

    universities = nearby[
        nearby["_amenity"] == "university"
    ]


    # --------------------------------------------------------
    # Nearest facility
    # --------------------------------------------------------

    nearby = nearby.sort_values(
        "distance_m"
    )

    nearest = nearby.iloc[0]


    # --------------------------------------------------------
    # Name
    # --------------------------------------------------------

    nearest_name = nearest[
        "name"
    ]

    if pd.isna(nearest_name):

        nearest_name = nearest[
            "name:en"
        ]


    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    results.append({

        "candidate_id":
            candidate_id,

        "route":
            route,

        "chainage_km":
            chainage,

        "education_within_1km":
            len(nearby),

        "schools_within_1km":
            len(schools),

        "colleges_within_1km":
            len(colleges),

        "universities_within_1km":
            len(universities),

        "nearest_education_distance_m":
            round(
                float(
                    nearest[
                        "distance_m"
                    ]
                ),
                2
            ),

        "nearest_education_distance_km":
            round(
                float(
                    nearest[
                        "distance_m"
                    ]
                ) / 1000,
                4
            ),

        "nearest_education_name":
            nearest_name,

        "nearest_education_type":
            nearest[
                "amenity"
            ],

    })


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

result = pd.DataFrame(
    results
)


# ============================================================
# SAVE CSV
# ============================================================

RESULTS.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    CSV_FILE,
    index=False
)


# ============================================================
# CREATE GIS OUTPUT
# ============================================================

result_gdf = stations[
    [
        "candidate_id",
        "geometry"
    ]
].merge(
    result,
    on="candidate_id",
    how="left"
)


result_gdf = gpd.GeoDataFrame(
    result_gdf,
    geometry="geometry",
    crs=stations.crs
)


if OUTPUT_FILE.exists():

    OUTPUT_FILE.unlink()


result_gdf.to_file(
    OUTPUT_FILE,
    layer="station_education",
    driver="GPKG"
)


# ============================================================
# ROUTE SUMMARY
# ============================================================

print()
print("=" * 80)
print("STATION EDUCATION SUMMARY")
print("=" * 80)


summary = (
    result
    .groupby("route")
    .agg(
        candidates=(
            "candidate_id",
            "count"
        ),

        candidates_with_education=(
            "education_within_1km",
            lambda x: (x > 0).sum()
        ),

        total_education_features=(
            "education_within_1km",
            "sum"
        ),

        total_schools=(
            "schools_within_1km",
            "sum"
        ),

        total_colleges=(
            "colleges_within_1km",
            "sum"
        ),

        total_universities=(
            "universities_within_1km",
            "sum"
        ),

        average_nearest_education_km=(
            "nearest_education_distance_km",
            "mean"
        ),

        minimum_nearest_education_km=(
            "nearest_education_distance_km",
            "min"
        )
    )
    .reset_index()
)


print(
    summary.to_string(
        index=False
    )
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("CSV:")
print(CSV_FILE)

print()
print("GeoPackage:")
print(OUTPUT_FILE)

print()
print(
    "Station education analysis completed successfully."
)