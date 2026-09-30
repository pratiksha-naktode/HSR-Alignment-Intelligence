from pathlib import Path
import geopandas as gpd
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE = Path(__file__).resolve().parent.parent

CORRIDORS = {
    "Route 1": BASE / "data/processed/Route_1_corridor_3_5m.gpkg",
    "Route 2": BASE / "data/processed/Route_2_corridor_3_5m.gpkg",
    "Route 3": BASE / "data/processed/Route_3_corridor_3_5m.gpkg",
}


# IMPORTANT:
# Your actual folder is named "ctiteria_dataset"
# (not "criteria_dataset")

CRITERIA_DIR = BASE / "ctiteria_dataset"

EDU = CRITERIA_DIR / "hotosm_ind_education_facilities_polygons_geojson.geojson"

WATER = CRITERIA_DIR / "Amrit_Sarovar_Water_Observatory_Ponds.geojsonl"

WETLAND = CRITERIA_DIR / "Bharatmaps_Parivesh_Wetland_Boundaries.geojsonl"

ESZ = CRITERIA_DIR / "Bharatmaps_Parivesh_Eco_Sensitive_Zones.geojsonl"

HIGHWAY = CRITERIA_DIR / "GatiShakti_MORTH_National_Highways.geojsonl"


# ============================================================
# OUTPUT
# ============================================================

OUT = BASE / "data/results"
OUT.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

def load(path):
    print(f"Loading: {path.name}")
    return gpd.read_file(path)


datasets = {
    "Educational Sector": load(EDU),
    "Waterbodies": load(WATER),
    "Wetlands": load(WETLAND),
    "Eco-sensitive Zones": load(ESZ),
    "Highways": load(HIGHWAY),
}


# ============================================================
# PROCESS
# ============================================================

rows = []


for route, corridor_path in CORRIDORS.items():

    print(f"\nProcessing {route}...")

    corridor = gpd.read_file(corridor_path)

    if corridor.crs is None:
        corridor = corridor.set_crs("EPSG:32643")

    corridor = corridor.to_crs("EPSG:32643")

    # --------------------------------------------------------
    # 3.5 m corridor
    # --------------------------------------------------------

    direct = corridor[["geometry"]].copy()

    # --------------------------------------------------------
    # 100 m fallback zone
    #
    # The corridor is already 3.5 m wide.
    # Therefore, we need the CENTERLINE to create an exact
    # 100 m distance zone.
    # --------------------------------------------------------

    # Shrink corridor back approximately to centerline by using
    # the original route centerline from RouteData.
    route_number = route.split()[-1]

    centerline_path = (
        BASE
        / f"RouteData/R{route_number}/R{route_number}/ROUTE {route_number}.shp"
    )

    if centerline_path.exists():

        centerline = gpd.read_file(centerline_path)

        if centerline.crs is None:
            centerline = centerline.set_crs("EPSG:4326")

        centerline = centerline.to_crs("EPSG:32643")

        influence = centerline.buffer(100).to_frame("geometry")
        influence = gpd.GeoDataFrame(
            influence,
            geometry="geometry",
            crs="EPSG:32643"
        )

    else:

        # Fallback if original centerline cannot be found.
        # This gives approximately 101.75 m from centerline.
        influence = corridor.buffer(100).to_frame("geometry")
        influence = gpd.GeoDataFrame(
            influence,
            geometry="geometry",
            crs="EPSG:32643"
        )

    # ========================================================
    # EACH CRITERION
    # ========================================================

    for criterion, data in datasets.items():

        print(f"  → {criterion}")

        # Reproject criterion dataset
        if data.crs is None:
            data_p = data.set_crs("EPSG:4326")
        else:
            data_p = data.copy()

        data_p = data_p.to_crs("EPSG:32643")

        # ----------------------------------------------------
        # DIRECT 3.5 m INTERSECTION
        # ----------------------------------------------------

        direct_join = gpd.sjoin(
            data_p,
            direct,
            predicate="intersects",
            how="inner"
        )

        direct_ids = set(direct_join.index)

        # ----------------------------------------------------
        # WITHIN 100 m OF CENTERLINE
        # ----------------------------------------------------

        near_join = gpd.sjoin(
            data_p,
            influence[["geometry"]],
            predicate="intersects",
            how="inner"
        )

        near_ids = set(near_join.index)

        direct_count = len(direct_ids)
        near_count = len(near_ids)

        # ----------------------------------------------------
        # FINAL FALLBACK LOGIC
        # ----------------------------------------------------

        if direct_count > 0:

            final_count = direct_count
            method = "DIRECT_3_5M"

        elif near_count > 0:

            final_count = near_count
            method = "WITHIN_100M_FALLBACK"

        else:

            final_count = 0
            method = "NONE_WITHIN_100M"

        rows.append({
            "route": route,
            "criterion": criterion,
            "direct_3_5m_count": direct_count,
            "within_100m_count": near_count,
            "final_count": final_count,
            "method": method
        })


# ============================================================
# CREATE RESULT TABLE
# ============================================================

result = pd.DataFrame(rows)


# ============================================================
# SAVE RESULT
# ============================================================

output_file = OUT / "proximity_fallback_100m_summary.csv"

result.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 80)
print("100 m FALLBACK RESULTS")
print("=" * 80)
print()

print(result.to_string(index=False))

print("\n")
print("=" * 80)
print("RESULT SAVED")
print("=" * 80)

print(output_file)