import geopandas as gpd
import os

os.makedirs("data/results", exist_ok=True)

for route in [1, 2, 3]:

    print(f"\nProcessing Route {route}...")

    # ---------------------------------------------------------
    # INPUTS
    # ---------------------------------------------------------

    wetland_file = (
        "data/processed/wetlands_route_area.geojsonl"
    )

    corridor_file = (
        f"data/processed/"
        f"Route_{route}_corridor_3_5m.gpkg"
    )

    output_file = (
        f"data/results/"
        f"Route_{route}_wetland_patch_details.csv"
    )

    # ---------------------------------------------------------
    # READ DATA
    # ---------------------------------------------------------

    wetlands = gpd.read_file(wetland_file)
    corridor = gpd.read_file(corridor_file)

    print(f"Wetland polygons loaded: {len(wetlands)}")

    # ---------------------------------------------------------
    # PROJECT TO METRIC CRS
    # ---------------------------------------------------------

    wetlands = wetlands.to_crs("EPSG:32643")
    corridor = corridor.to_crs("EPSG:32643")

    # ---------------------------------------------------------
    # GET THE 3.5 m FOOTPRINT
    # ---------------------------------------------------------

    footprint = corridor.geometry.unary_union

    # ---------------------------------------------------------
    # FIND WETLANDS INTERSECTING THE FOOTPRINT
    # ---------------------------------------------------------

    candidate = wetlands[
        wetlands.geometry.intersects(footprint)
    ].copy()

    print(
        f"Wetland patches intersecting "
        f"3.5 m footprint: {len(candidate)}"
    )

    # ---------------------------------------------------------
    # CALCULATE INTERSECTION AREA
    # ---------------------------------------------------------

    candidate["intersection_geometry"] = (
        candidate.geometry.intersection(footprint)
    )

    candidate["affected_area_m2"] = (
        candidate["intersection_geometry"].area
    )

    # Remove zero-area intersections
    candidate = candidate[
        candidate["affected_area_m2"] > 0
    ].copy()

    # ---------------------------------------------------------
    # PATCH ID
    # ---------------------------------------------------------

    candidate["wetland_patch_id"] = range(
        1,
        len(candidate) + 1
    )

    # ---------------------------------------------------------
    # CHAINAGE
    # ---------------------------------------------------------

    # Find the closest point on the HSR centerline
    centerline_file = (
        f"data/processed/"
        f"Route_{route}_centerline.gpkg"
    )

    centerline = gpd.read_file(
        centerline_file
    ).to_crs("EPSG:32643")

    centerline_geom = centerline.geometry.unary_union

    candidate["intersection_centroid"] = (
        candidate["intersection_geometry"].centroid
    )

    candidate["chainage_km"] = (
        candidate["intersection_centroid"]
        .apply(
            lambda point:
            centerline_geom.project(point) / 1000
        )
    )

    # ---------------------------------------------------------
    # LATITUDE / LONGITUDE
    # ---------------------------------------------------------

    centroids = gpd.GeoSeries(
        candidate["intersection_centroid"],
        crs="EPSG:32643"
    ).to_crs("EPSG:4326")

    candidate["latitude"] = centroids.y
    candidate["longitude"] = centroids.x

    # ---------------------------------------------------------
    # m² → km²
    # ---------------------------------------------------------

    candidate["calculation"] = (
        candidate["affected_area_m2"]
        .apply(
            lambda x:
            f"{x:.6f} / 1,000,000"
        )
    )

    candidate["affected_area_km2"] = (
        candidate["affected_area_m2"]
        / 1_000_000
    )

    # ---------------------------------------------------------
    # OUTPUT TABLE
    # ---------------------------------------------------------

    output = candidate[
        [
            "wetland_patch_id",
            "wetname",
            "wetcode",
            "level1",
            "level2",
            "level3",
            "descr",
            "chainage_km",
            "latitude",
            "longitude",
            "affected_area_m2",
            "calculation",
            "affected_area_km2",
        ]
    ].copy()

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    output.to_csv(
        output_file,
        index=False
    )

    # ---------------------------------------------------------
    # VERIFY TOTAL
    # ---------------------------------------------------------

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
print("WETLAND DETAILS COMPLETE")
print("================================")