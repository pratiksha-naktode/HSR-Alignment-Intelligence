import geopandas as gpd
import pandas as pd
import os

os.makedirs("data/results", exist_ok=True)

WATERBODY_FILE = (
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset"
    r"\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"
)

# ---------------------------------------------------------
# LOAD WATERBODY POINTS
# ---------------------------------------------------------

print("Loading waterbody dataset...")

water = gpd.read_file(WATERBODY_FILE)

print(f"Waterbody records: {len(water)}")

# Project to metric CRS
water = water.to_crs("EPSG:32643")

# ---------------------------------------------------------
# PROCESS EACH ROUTE
# ---------------------------------------------------------

for route in [1, 2, 3]:

    print(f"\nProcessing Route {route}...")

    centerline_file = (
        f"data/processed/"
        f"Route_{route}_centerline.gpkg"
    )

    centerline = gpd.read_file(centerline_file)

    centerline = centerline.to_crs("EPSG:32643")

    route_geom = centerline.geometry.union_all()

    # -----------------------------------------------------
    # CALCULATE DISTANCE TO ROUTE
    # -----------------------------------------------------

    water["distance_m"] = (
        water.geometry.distance(route_geom)
    )

    water["distance_km"] = (
        water["distance_m"] / 1000
    )

    # -----------------------------------------------------
    # SORT BY DISTANCE
    # -----------------------------------------------------

    nearest = water.sort_values(
        "distance_m"
    ).head(20).copy()

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    output = nearest[
        [
            "Sarovar_ID",
            "Name_of_Sarovar",
            "Village",
            "District",
            "State",
            "distance_m",
            "distance_km",
        ]
    ].copy()

    output.insert(
        0,
        "route",
        f"Route {route}"
    )

    output_file = (
        f"data/results/"
        f"Route_{route}_nearest_waterbodies.csv"
    )

    output.to_csv(
        output_file,
        index=False
    )

    # -----------------------------------------------------
    # PRINT NEAREST
    # -----------------------------------------------------

    nearest_row = output.iloc[0]

    print(
        f"Nearest waterbody: "
        f"{nearest_row['Name_of_Sarovar']}"
    )

    print(
        f"Distance: "
        f"{nearest_row['distance_m']:.2f} m "
        f"({nearest_row['distance_km']:.4f} km)"
    )

    print(
        f"Saved: {output_file}"
    )


print("\n================================")
print("WATERBODY PROXIMITY COMPLETE")
print("================================")