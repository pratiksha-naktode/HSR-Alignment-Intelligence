import geopandas as gpd
import os

os.makedirs("data/results", exist_ok=True)

for route in [1, 2, 3]:

    print(f"\nProcessing Route {route}...")

    # ---------------------------------------------------------
    # INPUT FILE
    # ---------------------------------------------------------

    if route == 1:
        input_file = (
            "data/processed/"
            "Route_1_lulc_intersections_corrected.gpkg"
        )
    else:
        input_file = (
            f"data/processed/"
            f"Route_{route}_lulc_intersections_final.gpkg"
        )

    output_file = (
        f"data/results/"
        f"Route_{route}_agriculture_patch_details.csv"
    )

    # ---------------------------------------------------------
    # READ EXISTING PROCESSED DATA
    # ---------------------------------------------------------

    gdf = gpd.read_file(input_file)

    print(f"Loaded {len(gdf)} LULC intersection records")

    # ---------------------------------------------------------
    # HANDLE DIFFERENT COLUMN NAMES
    # ---------------------------------------------------------

    if "Level_I" in gdf.columns:
        landuse_column = "Level_I"
    elif "level_i" in gdf.columns:
        landuse_column = "level_i"
    else:
        raise KeyError(
            f"No Level I land-use column found for Route {route}"
        )

    # ---------------------------------------------------------
    # SELECT AGRICULTURE
    # ---------------------------------------------------------

    agriculture = gdf[
        gdf[landuse_column]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        == "agriculture"
    ].copy()

    print(
        f"Agriculture patches found: "
        f"{len(agriculture)}"
    )

    # ---------------------------------------------------------
    # PATCH ID
    # ---------------------------------------------------------

    agriculture["agriculture_patch_id"] = range(
        1,
        len(agriculture) + 1
    )

    # ---------------------------------------------------------
    # CHAINAGE
    # ---------------------------------------------------------

    if "first_sample_km" in agriculture.columns:

        agriculture["chainage_km"] = (
            agriculture["first_sample_km"]
        )

    elif "sample_distance_m" in agriculture.columns:

        agriculture["chainage_km"] = (
            agriculture["sample_distance_m"] / 1000
        )

    else:
        agriculture["chainage_km"] = None

    # ---------------------------------------------------------
    # AFFECTED AREA
    # ---------------------------------------------------------

    agriculture["affected_area_m2"] = (
        agriculture["impact_area_m2"]
    )

    # ---------------------------------------------------------
    # CALCULATION DISPLAY
    # ---------------------------------------------------------

    agriculture["calculation"] = (
        agriculture["affected_area_m2"]
        .apply(
            lambda x:
            f"{x:.6f} / 1,000,000"
        )
    )

    # ---------------------------------------------------------
    # CONVERT m² → km²
    # ---------------------------------------------------------

    agriculture["affected_area_km2"] = (
        agriculture["affected_area_m2"]
        / 1_000_000
    )

    # ---------------------------------------------------------
    # COORDINATES
    # ---------------------------------------------------------

    if (
        "sample_latitude" in agriculture.columns
        and "sample_longitude" in agriculture.columns
    ):

        latitude = agriculture["sample_latitude"]
        longitude = agriculture["sample_longitude"]

    else:

        # R1 does not have sample latitude/longitude,
        # so calculate them from the intersection geometry.

        centroid = agriculture.geometry.centroid

        latitude = centroid.y
        longitude = centroid.x

    agriculture["latitude"] = latitude
    agriculture["longitude"] = longitude

    # ---------------------------------------------------------
    # OUTPUT TABLE
    # ---------------------------------------------------------

    output = agriculture[
        [
            "agriculture_patch_id",
            "chainage_km",
            "latitude",
            "longitude",
            "affected_area_m2",
            "calculation",
            "affected_area_km2",
        ]
    ].copy()

    # ---------------------------------------------------------
    # SAVE CSV
    # ---------------------------------------------------------

    output.to_csv(
        output_file,
        index=False
    )

    # ---------------------------------------------------------
    # VERIFY TOTAL
    # ---------------------------------------------------------

    total_m2 = output["affected_area_m2"].sum()

    total_km2 = output["affected_area_km2"].sum()

    print(
        f"Route {route}: "
        f"{len(output)} patches | "
        f"{total_m2:.3f} m² | "
        f"{total_km2:.8f} km²"
    )

    print(
        f"Saved: {output_file}"
    )

print("\n================================")
print("AGRICULTURE DETAILS COMPLETE")
print("================================")