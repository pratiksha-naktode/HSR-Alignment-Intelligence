import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import Point


# ============================================================
# HSR ROUTE OPTIMIZATION
# ROUTE CHAINAGE GENERATION
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"

OUTPUT = (
    PROCESSED /
    "route_chainage_points.gpkg"
)


# ============================================================
# SETTINGS
# ============================================================

METRIC_CRS = "EPSG:32643"
OUTPUT_CRS = "EPSG:4326"

CHAINAGE_INTERVAL_M = 1000


# ============================================================
# ROUTES
# ============================================================

route_files = {
    "Route 1":
        PROCESSED / "Route_1_centerline.gpkg",

    "Route 2":
        PROCESSED / "Route_2_centerline.gpkg",

    "Route 3":
        PROCESSED / "Route_3_centerline.gpkg",
}


# ============================================================
# FUNCTION
# ============================================================

def generate_chainage_points(
    route_name,
    file_path
):

    print(
        f"\nProcessing {route_name}..."
    )

    gdf = gpd.read_file(
        file_path
    )

    if gdf.empty:
        raise ValueError(
            f"{route_name} has no geometry."
        )

    # Convert to metric CRS
    gdf = gdf.to_crs(
        METRIC_CRS
    )

    # Combine geometry if necessary
    line = gdf.geometry.unary_union

    if line.geom_type == "MultiLineString":

        # Merge connected segments
        from shapely.ops import linemerge

        line = linemerge(line)

    if line.geom_type != "LineString":

        raise ValueError(
            f"{route_name} geometry is "
            f"{line.geom_type}, expected LineString."
        )

    route_length_m = line.length

    print(
        f"Route length: "
        f"{route_length_m / 1000:.3f} km"
    )

    # Generate distances
    distances = list(
        range(
            0,
            int(route_length_m),
            CHAINAGE_INTERVAL_M
        )
    )

    # Ensure final point exists
    if (
        not distances
        or distances[-1] != route_length_m
    ):

        distances.append(
            route_length_m
        )

    records = []

    for distance_m in distances:

        point = line.interpolate(
            distance_m
        )

        records.append({

            "route": route_name,

            "chainage_m":
                round(
                    distance_m,
                    3
                ),

            "chainage_km":
                round(
                    distance_m / 1000,
                    3
                ),

            "distance_from_end_km":
                round(
                    (
                        route_length_m
                        - distance_m
                    ) / 1000,
                    3
                ),

            "geometry": point
        })

    result = gpd.GeoDataFrame(
        records,
        crs=METRIC_CRS
    )

    # Convert to WGS84
    result = result.to_crs(
        OUTPUT_CRS
    )

    # Add coordinates
    result[
        "longitude"
    ] = result.geometry.x.round(6)

    result[
        "latitude"
    ] = result.geometry.y.round(6)

    return result


# ============================================================
# PROCESS ALL ROUTES
# ============================================================

all_points = []

for route_name, file_path in route_files.items():

    if not file_path.exists():

        raise FileNotFoundError(
            f"Missing route file:\n{file_path}"
        )

    route_points = generate_chainage_points(
        route_name,
        file_path
    )

    all_points.append(
        route_points
    )


# ============================================================
# COMBINE
# ============================================================

chainage = gpd.GeoDataFrame(
    pd.concat(
        all_points,
        ignore_index=True
    ),
    crs=OUTPUT_CRS
)


# ============================================================
# ADD UNIQUE ID
# ============================================================

chainage.insert(
    0,
    "chainage_id",
    range(
        1,
        len(chainage) + 1
    )
)


# ============================================================
# SAVE
# ============================================================

if OUTPUT.exists():
    OUTPUT.unlink()


chainage.to_file(
    OUTPUT,
    layer="route_chainage",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("CHAINAGE GENERATION COMPLETE")
print("=" * 80)

summary = (
    chainage
    .groupby("route")
    .agg(
        points=("chainage_id", "count"),
        max_chainage_km=("chainage_km", "max")
    )
    .reset_index()
)

print(
    summary.to_string(
        index=False
    )
)

print("\nOutput:")
print(OUTPUT)

print("\nCRS:")
print(chainage.crs)