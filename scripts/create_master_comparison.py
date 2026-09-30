from pathlib import Path
import pandas as pd

RESULTS = Path("data/results")
OUTPUT = RESULTS / "route_comparison_raw.csv"

RESULTS.mkdir(parents=True, exist_ok=True)

# ================================================================
# VERIFIED ROUTE LENGTHS
# ================================================================

route_lengths = {
    "Route 1": 788.78495,
    "Route 2": 789.90222,
    "Route 3": 799.26005,
}

# ================================================================
# LOAD VERIFIED GIS RESULTS
# ================================================================

education = pd.read_csv(
    RESULTS / "educational_sector_impact_100m.csv"
)

wetland = pd.read_csv(
    RESULTS / "wetland_impact_summary.csv"
)

esz = pd.read_csv(
    RESULTS / "esz_impact_summary.csv"
)

highway = pd.read_csv(
    RESULTS / "highway_impact_summary.csv"
)

waterbody = pd.read_csv(
    RESULTS / "waterbody_impact_summary.csv"
)

# ================================================================
# STANDARDIZE ROUTE NAMES
# ================================================================

for df in [education, wetland, esz, highway, waterbody]:
    df["route"] = df["route"].astype(str).str.strip()

# ================================================================
# BUILD MASTER DATASET
# ================================================================

routes = ["Route 1", "Route 2", "Route 3"]

rows = []

for route in routes:

    # -----------------------------
    # Educational Sector
    # -----------------------------
    edu_row = education[
        education["route"] == route
    ].iloc[0]

    # -----------------------------
    # Wetlands
    # -----------------------------
    wetland_row = wetland[
        wetland["route"] == route
    ].iloc[0]

    wetland_area_m2 = float(
        wetland_row["wetland_area_m2"]
    )

    wetland_area_km2 = wetland_area_m2 / 1_000_000

    # -----------------------------
    # ESZ
    # -----------------------------
    esz_row = esz[
        esz["route"] == route
    ].iloc[0]

    nearest_esz_m = float(
        esz_row["nearest_esz_distance_m"]
    )

    nearest_esz_km = nearest_esz_m / 1000

    # -----------------------------
    # Highway
    # -----------------------------
    highway_row = highway[
        highway["route"] == route
    ].iloc[0]

    # -----------------------------
    # Waterbody
    # -----------------------------
    waterbody_row = waterbody[
        waterbody["route"] == route
    ].iloc[0]

    # ============================================================
    # MASTER ROW
    # ============================================================

    rows.append({
        "route": route,

        # Route length
        "route_length_km": route_lengths[route],

        # LULC
        # Classification mapping is NOT verified yet.
        "forest_area_km2": None,
        "agriculture_area_km2": None,
        "built_up_area_km2": None,

        # Educational Sector
        "educational_sector_count": int(
            edu_row["final_education_count"]
        ),
        "educational_types": edu_row["educational_types"],

        # Wetlands
        "wetland_intersection_count": int(
            wetland_row["wetland_count"]
        ),
        "wetland_area_m2": wetland_area_m2,
        "wetland_area_km2": wetland_area_km2,

        # Waterbodies
        "waterbody_intersection_count": int(
            waterbody_row["waterbody_count"]
        ),

        # ESZ
        "esz_intersection_count": int(
            esz_row["intersecting_esz_count"]
        ),
        "nearest_esz_distance_km": nearest_esz_km,
        "nearest_esz_name": esz_row["nearest_esz_name"],

        # Highways
        "highway_total_intersections": int(
            highway_row["total_intersections"]
        ),
        "highway_unique_road_count": int(
            highway_row["unique_road_count"]
        ),
        "national_highway_crossings": int(
            highway_row["nh_crossings"]
        ),
        "state_highway_crossings": int(
            highway_row["sh_crossings"]
        ),
        "mdr_crossings": None,

        # Preserve actual source categories
        "state_expressway_crossings": int(
            highway_row["state_expressway_crossings"]
        ),
        "other_major_road_crossings": int(
            highway_row["other_major_road_crossings"]
        ),

        # Status
        "lulc_status": (
            "PENDING: verified DN -> lc_code/class mapping required"
        ),
        "mdr_status": highway_row["mdr_status"],
        "waterbody_status": (
            "Point dataset: intersection count available; "
            "area in km2 cannot be derived"
        ),
    })

# ================================================================
# CREATE DATAFRAME
# ================================================================

df = pd.DataFrame(rows)

# ================================================================
# SAVE
# ================================================================

df.to_csv(OUTPUT, index=False)

# ================================================================
# DISPLAY
# ================================================================

print("=" * 80)
print("MASTER RAW ROUTE COMPARISON")
print("=" * 80)

print("\nSaved:")
print(OUTPUT.resolve())

print("\nShape:", df.shape)

print("\nData:")
print(df.to_string(index=False))

print("\n" + "=" * 80)
print("CRITERIA STATUS")
print("=" * 80)

print("Route length       : VERIFIED")
print("Educational Sector : VERIFIED - 100 m centerline")
print("Wetlands           : VERIFIED - 3.5 m footprint")
print("Waterbody          : VERIFIED - count only")
print("ESZ                : VERIFIED")
print("Highways           : VERIFIED")
print("Forest             : PENDING")
print("Agriculture        : PENDING")
print("Built-up           : PENDING")

print("\nNo LULC DN classification has been assumed.")
print("No MDR classification has been fabricated.")