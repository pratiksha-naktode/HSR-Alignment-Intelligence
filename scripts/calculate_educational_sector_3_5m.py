import geopandas as gpd
import pandas as pd
from pathlib import Path

PROJECT = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

EDUCATION = Path(
    r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset"
    r"\hotosm_ind_education_facilities_polygons_geojson.geojson"
)

ROUTES = PROJECT / "data" / "processed"
OUTPUT = PROJECT / "data" / "results"
OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 75)
print("EDUCATIONAL SECTOR IMPACT — 3.5 m + 100 m CENTERLINE")
print("=" * 75)

# ==============================================================
# LOAD EDUCATION DATA
# ==============================================================

print("\nLoading education dataset...")

education = gpd.read_file(EDUCATION)

print("Education features:", len(education))
print("Education CRS:", education.crs)

education = education.to_crs("EPSG:32643")

summary = []
details = []

# ==============================================================
# PROCESS ROUTES
# ==============================================================

for route_no in [1, 2, 3]:

    print(f"\n{'=' * 60}")
    print(f"Processing Route {route_no}")
    print(f"{'=' * 60}")

    # ----------------------------------------------------------
    # Load existing 3.5 m corridor
    # ----------------------------------------------------------

    corridor_file = (
        ROUTES / f"Route_{route_no}_corridor_3_5m.gpkg"
    )

    corridor = gpd.read_file(corridor_file)

    if corridor.crs != education.crs:
        corridor = corridor.to_crs(education.crs)

    corridor_geom = corridor.geometry.iloc[0]

    # ----------------------------------------------------------
    # 1. DIRECT 3.5 m INTERSECTION
    # ----------------------------------------------------------

    direct_candidates = education[
        education.intersects(corridor_geom)
    ].copy()

    direct_count = len(direct_candidates)

    print(
        f"Direct 3.5 m education features: "
        f"{direct_count}"
    )

    # ----------------------------------------------------------
    # 2. 100 m FROM CENTERLINE
    # ----------------------------------------------------------
    #
    # We need the ORIGINAL route centerline.
    # The existing RouteData files are used here.
    # ----------------------------------------------------------

    route_file = (
        Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT")
        / "RouteData"
        / f"R{route_no}"
        / f"R{route_no}"
        / f"ROUTE {route_no}.shp"
    )

    print(f"Centerline file: {route_file}")

    centerline = gpd.read_file(route_file)

    if centerline.crs is None:
        centerline = centerline.set_crs("EPSG:4326")

    centerline = centerline.to_crs("EPSG:32643")

    centerline_geom = centerline.geometry.unary_union

    # Exact 100 m zone from CENTERLINE
    buffer_100m = centerline_geom.buffer(100)

    # ----------------------------------------------------------
    # Find education features within 100 m
    # ----------------------------------------------------------

    nearby = education[
        education.intersects(buffer_100m)
    ].copy()

    nearby_count = len(nearby)

    print(
        f"Education features within 100 m: "
        f"{nearby_count}"
    )

    # ----------------------------------------------------------
    # Calculate actual minimum distance
    # ----------------------------------------------------------

    if nearby_count > 0:

        nearby["distance_from_centerline_m"] = (
            nearby.geometry.distance(centerline_geom)
        )

    # ----------------------------------------------------------
    # FINAL EDUCATION COUNT
    #
    # Updated requirement:
    # schools/colleges/etc. within 100 m
    # ----------------------------------------------------------

    final_count = nearby_count

    # ----------------------------------------------------------
    # Education types
    # ----------------------------------------------------------

    if nearby_count > 0 and "amenity" in nearby.columns:

        types = (
            nearby["amenity"]
            .dropna()
            .astype(str)
            .value_counts()
            .to_dict()
        )

        type_text = "; ".join(
            f"{k}: {v}"
            for k, v in types.items()
        )

    else:

        types = {}
        type_text = ""

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------

    summary.append({
        "route": f"Route {route_no}",
        "direct_3_5m_count": direct_count,
        "within_100m_centerline_count": nearby_count,
        "final_education_count": final_count,
        "educational_types": type_text
    })

    # ----------------------------------------------------------
    # Detailed records
    # ----------------------------------------------------------

    for _, row in nearby.iterrows():

        details.append({
            "route": f"Route {route_no}",
            "name": row.get("name"),
            "name_en": row.get("name:en"),
            "amenity": row.get("amenity"),
            "building": row.get("building"),
            "operator_type": row.get("operator:type"),
            "capacity": row.get("capacity:persons"),
            "city": row.get("addr:city"),
            "osm_id": row.get("osm_id"),
            "distance_from_centerline_m": row.get(
                "distance_from_centerline_m"
            )
        })


# ==============================================================
# SAVE RESULTS
# ==============================================================

summary_df = pd.DataFrame(summary)
details_df = pd.DataFrame(details)

summary_file = (
    OUTPUT / "educational_sector_impact_100m.csv"
)

details_file = (
    OUTPUT / "educational_sector_details_100m.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)

details_df.to_csv(
    details_file,
    index=False
)


# ==============================================================
# DISPLAY
# ==============================================================

print("\n")
print("=" * 75)
print("FINAL EDUCATIONAL SECTOR RESULTS — 100 m CENTERLINE")
print("=" * 75)

print(
    summary_df.to_string(index=False)
)

print("\nSaved:")
print(summary_file)
print(details_file)

print("\n")
print("=" * 75)
print("EDUCATION TYPE BREAKDOWN")
print("=" * 75)

for route_no in [1, 2, 3]:

    route_name = f"Route {route_no}"

    route_data = details_df[
        details_df["route"] == route_name
    ]

    print(f"\n{route_name}")

    if len(route_data) == 0:

        print("No education features within 100 m.")

    else:

        print(
            route_data["amenity"]
            .value_counts(dropna=False)
            .to_string()
        )