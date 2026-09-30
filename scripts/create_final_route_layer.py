import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# FINAL ROUTE GIS LAYER
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

RESULTS = BASE / "data" / "results"
PROCESSED = BASE / "data" / "processed"

OUTPUT = (
    PROCESSED /
    "final_route_alternatives.gpkg"
)


# ============================================================
# INPUT ROUTES
# ============================================================

route_files = {
    "Route 1": (
        PROCESSED / "Route_1_centerline.gpkg"
    ),
    "Route 2": (
        PROCESSED / "Route_2_centerline.gpkg"
    ),
    "Route 3": (
        PROCESSED / "Route_3_centerline.gpkg"
    ),
}


DECISION_FILE = (
    RESULTS /
    "final_route_decision_dataset.csv"
)


# ============================================================
# LOAD DECISION DATA
# ============================================================

decision = pd.read_csv(
    DECISION_FILE
)


required_columns = [
    "route",
    "topsis_score",
    "topsis_rank",
]


for column in required_columns:

    if column not in decision.columns:

        raise ValueError(
            f"Missing decision column: {column}"
        )


# ============================================================
# LOAD ROUTES
# ============================================================

routes = []

for route_name, file_path in route_files.items():

    if not file_path.exists():

        raise FileNotFoundError(
            f"Route file not found:\n{file_path}"
        )

    gdf = gpd.read_file(
        file_path
    )

    if gdf.empty:

        raise ValueError(
            f"{route_name} contains no geometry."
        )

    gdf = gdf[
        ["geometry"]
    ].copy()

    gdf["route"] = route_name

    routes.append(
        gdf
    )


# ============================================================
# COMBINE ROUTES
# ============================================================

final_routes = gpd.GeoDataFrame(
    pd.concat(
        routes,
        ignore_index=True
    ),
    crs=routes[0].crs
)


# ============================================================
# ATTACH DECISION RESULTS
# ============================================================

decision_columns = [
    "route",
    "topsis_score",
    "topsis_rank",
]


final_routes = final_routes.merge(
    decision[
        decision_columns
    ],
    on="route",
    how="left"
)


# ============================================================
# ADD FINAL STATUS
# ============================================================

final_routes[
    "analysis_status"
] = "Alternative"


final_routes.loc[
    final_routes["topsis_rank"] == 1,
    "analysis_status"
] = "Baseline TOPSIS Rank 1"


# ============================================================
# ADD ROUTE LENGTH
# ============================================================

# Work in metric CRS for length calculation.

metric_routes = final_routes.to_crs(
    "EPSG:32643"
)

metric_routes[
    "route_length_km"
] = (
    metric_routes.geometry.length
    / 1000.0
)


# ============================================================
# RETURN TO WGS84
# ============================================================

final_routes = metric_routes.to_crs(
    "EPSG:4326"
)


# ============================================================
# ROUND VALUES
# ============================================================

final_routes[
    "topsis_score"
] = final_routes[
    "topsis_score"
].round(8)


final_routes[
    "route_length_km"
] = final_routes[
    "route_length_km"
].round(6)


# ============================================================
# SAVE
# ============================================================

if OUTPUT.exists():

    OUTPUT.unlink()


final_routes.to_file(
    OUTPUT,
    layer="route_alternatives",
    driver="GPKG"
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 80)
print("FINAL ROUTE GIS LAYER")
print("=" * 80)

print(
    final_routes[
        [
            "route",
            "route_length_km",
            "topsis_score",
            "topsis_rank",
            "analysis_status",
        ]
    ].to_string(
        index=False
    )
)

print("\nSaved to:")
print(OUTPUT)

print("\nCRS:")
print(final_routes.crs)

print("\nFinal route GIS layer created successfully.")