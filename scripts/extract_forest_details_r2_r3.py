import geopandas as gpd
import os

os.makedirs("data/results", exist_ok=True)

for route in [2, 3]:

    print(f"\nProcessing Route {route}...")

    input_file = (
        f"data/processed/"
        f"Route_{route}_lulc_intersections_final.gpkg"
    )

    output_file = (
        f"data/results/"
        f"Route_{route}_forest_patch_details.csv"
    )

    gdf = gpd.read_file(input_file)

    # Route 2/3 use lowercase 'level_i'
    forest = gdf[
        gdf["level_i"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        == "forest"
    ].copy()

    forest["forest_patch_id"] = range(1, len(forest) + 1)

    forest["chainage_km"] = (
        forest["sample_distance_m"] / 1000
    )

    forest["affected_area_m2"] = (
        forest["impact_area_m2"]
    )

    forest["calculation"] = forest[
        "affected_area_m2"
    ].apply(
        lambda x: f"{x:.6f} / 1,000,000"
    )

    forest["affected_area_km2"] = (
        forest["affected_area_m2"] / 1_000_000
    )

    output = forest[
        [
            "forest_patch_id",
            "chainage_km",
            "sample_latitude",
            "sample_longitude",
            "affected_area_m2",
            "calculation",
            "affected_area_km2",
        ]
    ]

    output.to_csv(
        output_file,
        index=False
    )

    total_m2 = output["affected_area_m2"].sum()
    total_km2 = output["affected_area_km2"].sum()

    print(
        f"Route {route}: "
        f"{len(output)} patches | "
        f"{total_m2:.3f} m² | "
        f"{total_km2:.8f} km²"
    )

    print(f"Saved: {output_file}")

print("\n================================")
print("FOREST DETAILS COMPLETE")
print("================================")