import geopandas as gpd
import pandas as pd
from pathlib import Path


# =============================================================
# INPUT DATA
# =============================================================

HIGHWAY_FILE = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset"
    r"\GatiShakti_MORTH_National_Highways.geojsonl"
)

ROUTES = {
    "Route 1": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_1_corridor_3_5m.gpkg"
    ),
    "Route 2": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_2_corridor_3_5m.gpkg"
    ),
    "Route 3": Path(
        r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\processed"
        r"\Route_3_corridor_3_5m.gpkg"
    ),
}


# =============================================================
# OUTPUT
# =============================================================

OUTPUT_DIR = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization\data\results"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =============================================================
# COMBINED ROUTE BOUNDING BOX
# =============================================================

BBOX = (
    72.8369,
    17.0434,
    78.4679,
    19.1907,
)


# =============================================================
# LOAD HIGHWAY DATA
# =============================================================

print("Loading highway dataset...")

highways = gpd.read_file(
    HIGHWAY_FILE,
    bbox=BBOX
)

print(f"Highway candidates: {len(highways)}")


# Project to metric CRS
highways = highways.to_crs(32643)


# =============================================================
# STORAGE
# =============================================================

summary = []
details = []


# =============================================================
# PROCESS EACH ROUTE
# =============================================================

for route_name, route_file in ROUTES.items():

    print(f"\nProcessing {route_name}...")

    # ---------------------------------------------------------
    # Load 3.5 m corridor
    # ---------------------------------------------------------

    corridor = gpd.read_file(
        route_file
    ).to_crs(32643)

    # ---------------------------------------------------------
    # Spatial intersection
    # ---------------------------------------------------------

    intersections = gpd.sjoin(
        highways,
        corridor,
        predicate="intersects",
        how="inner",
    )

    # ---------------------------------------------------------
    # HIGHWAY CLASSIFICATION
    # ---------------------------------------------------------

    road_types = (
        intersections["road_type"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # National Highway
    nh_count = (
        road_types == "National Highway"
    ).sum()

    # State Highway
    sh_count = (
        road_types == "State Highway"
    ).sum()

    # State Expressway
    state_expressway_count = (
        road_types == "State Expressway"
    ).sum()

    # Other Major Road
    other_major_road_count = (
        road_types == "Other Major Road"
    ).sum()

    # Total spatial intersections
    total_intersections = len(intersections)

    # MDR cannot be identified reliably
    # from the supplied dataset.
    mdr_count = None

    # ---------------------------------------------------------
    # UNIQUE ROAD COUNT
    # ---------------------------------------------------------

    valid_names = (
        intersections["road_name"]
        .dropna()
        .astype(str)
    )

    unique_road_count = (
        valid_names.nunique()
    )

    # ---------------------------------------------------------
    # ROAD TYPE DISTRIBUTION
    # ---------------------------------------------------------

    road_type_counts = (
        road_types
        .value_counts()
        .to_dict()
    )

    # ---------------------------------------------------------
    # STATE DISTRIBUTION
    # ---------------------------------------------------------

    state_counts = (
        intersections["state_ut"]
        .fillna("Unknown")
        .value_counts()
        .to_dict()
    )

    # ---------------------------------------------------------
    # ROUTE SUMMARY
    # ---------------------------------------------------------

    summary.append({
        "route": route_name,

        # Required highway categories
        "nh_crossings": nh_count,
        "sh_crossings": sh_count,
        "mdr_crossings": mdr_count,

        # Source categories kept separately
        "state_expressway_crossings": (
            state_expressway_count
        ),

        "other_major_road_crossings": (
            other_major_road_count
        ),

        # Total
        "total_intersections": (
            total_intersections
        ),

        # Supporting information
        "unique_road_count": (
            unique_road_count
        ),

        "road_type_counts": (
            str(road_type_counts)
        ),

        "state_counts": (
            str(state_counts)
        ),

        # Data limitation
        "mdr_status": (
            "Not identifiable from supplied "
            "GatiShakti/MORTH dataset"
        ),
    })

    # =========================================================
    # INDIVIDUAL CROSSING DETAILS
    # =========================================================

    cols = [
        "id",
        "road_name",
        "road_type",
        "lane_statu",
        "state_ut",
        "gis_length",
        "category",
        "level_1",
        "level_2",
        "level_3",
        "level_4",
        "level_5",
        "status",
    ]

    available_cols = [
        c
        for c in cols
        if c in intersections.columns
    ]

    detail = intersections[
        available_cols
    ].copy()

    detail.insert(
        0,
        "route",
        route_name
    )

    # Store the exact source classification
    detail["analysis_class"] = road_types.values

    details.append(detail)

    # ---------------------------------------------------------
    # PRINT ROUTE RESULTS
    # ---------------------------------------------------------

    print(
        f"Total intersections       : "
        f"{total_intersections}"
    )

    print(
        f"National Highway (NH)     : "
        f"{nh_count}"
    )

    print(
        f"State Highway (SH)        : "
        f"{sh_count}"
    )

    print(
        f"State Expressway          : "
        f"{state_expressway_count}"
    )

    print(
        f"Other Major Road          : "
        f"{other_major_road_count}"
    )

    print(
        "MDR                       : "
        "Not identifiable"
    )

    print(
        f"Unique named roads        : "
        f"{unique_road_count}"
    )


# =============================================================
# CREATE DATAFRAMES
# =============================================================

summary_df = pd.DataFrame(
    summary
)

details_df = pd.concat(
    details,
    ignore_index=True
)


# =============================================================
# OUTPUT FILES
# =============================================================

summary_file = (
    OUTPUT_DIR /
    "highway_impact_summary.csv"
)

details_file = (
    OUTPUT_DIR /
    "highway_impact_details.csv"
)


summary_df.to_csv(
    summary_file,
    index=False
)

details_df.to_csv(
    details_file,
    index=False
)


# =============================================================
# FINAL OUTPUT
# =============================================================

print("\n========================================")
print("HIGHWAY ANALYSIS COMPLETED")
print("========================================")

print("\nSummary file:")
print(summary_file)

print("\nDetails file:")
print(details_file)

print("\nFinal Highway Summary:")

print(
    summary_df[
        [
            "route",
            "nh_crossings",
            "sh_crossings",
            "mdr_crossings",
            "state_expressway_crossings",
            "other_major_road_crossings",
            "total_intersections",
        ]
    ].to_string(index=False)
)