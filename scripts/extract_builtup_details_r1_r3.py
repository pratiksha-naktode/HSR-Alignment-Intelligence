import geopandas as gpd
import os

os.makedirs("data/results", exist_ok=True)

for route in [1, 2, 3]:

    print(f"\nProcessing Route {route}...")

    # Input files
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
        f"Route_{route}_builtup_patch_details.csv"
    )

    # Read existing processed LULC data
    gdf = gpd.read_file(input_file)

    print(f"Loaded {len(gdf)} LULC intersection records")

    # Handle R1 vs R2/R3 column naming
    if "Level_I" in gdf.columns:
        landuse_column = "Level_I"
    elif "level_i" in gdf.columns:
        landuse_column = "level_i"
    else:
        raise KeyError(
            f"No Level I column found for Route {route}"
        )

    # Select Built-up
    builtup = gdf[
        gdf[landuse_column]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        == "built-up"
    ].copy()

    print(
        f"Built-up patches found: "
        f"{len(builtup)}"
    )

    # Patch ID
    builtup["builtup_patch_id"] = range(
        1,
        len(builtup) + 1
    )

    # Chainage
    if "first_sample_km" in builtup.columns:
        builtup["chainage_km"] = (
            builtup["first_sample_km"]
        )
    elif "sample_distance_m" in builtup.columns:
        builtup["chainage_km"] = (
            builtup["sample_distance_m"] / 1000
        )
    else:
        builtup["chainage_km"] = None

    # Affected area from existing 3.5 m footprint calculation
    builtup["affected_area_m2"] = (
        builtup["impact_area_m2"]
    )

    # Show calculation
    builtup["calculation"] = (
        builtup["affected_area_m2"]
        .apply(
            lambda x:
            f"{x:.6f} / 1,000,000"
        )
    )

    # Convert m² → km²
    builtup["affected_area_km2"] = (
        builtup["affected_area_m2"]
        / 1_000_000
    )

    # Coordinates
    if (
        "sample_latitude" in builtup.columns
        and "sample_longitude" in builtup.columns
    ):
        builtup["latitude"] = (
            builtup["sample_latitude"]
        )
        builtup["longitude"] = (
            builtup["sample_longitude"]
        )
    else:
        centroid = builtup.geometry.centroid

        builtup["latitude"] = centroid.y
        builtup["longitude"] = centroid.x

    # Final output table
    output = builtup[
        [
            "builtup_patch_id",
            "chainage_km",
            "latitude",
            "longitude",
            "affected_area_m2",
            "calculation",
            "affected_area_km2",
        ]
    ].copy()

    # Save
    output.to_csv(
        output_file,
        index=False
    )

    # Verify total
    total_m2 = (
        output["affected_area_m2"].sum()
    )

    total_km2 = (
        output["affected_area_km2"].sum()
    )

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
print("BUILT-UP DETAILS COMPLETE")
print("================================")