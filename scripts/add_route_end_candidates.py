import geopandas as gpd
import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION
# ADD EXACT ROUTE-END STATION CANDIDATES
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

PROCESSED = BASE / "data" / "processed"

INPUT_FILE = (
    PROCESSED /
    "station_candidates.gpkg"
)

OUTPUT_FILE = (
    PROCESSED /
    "station_candidates_final.gpkg"
)


# ============================================================
# LOAD
# ============================================================

candidates = gpd.read_file(
    INPUT_FILE,
    layer="station_candidates"
)

print("=" * 80)
print("ADDING EXACT ROUTE-END CANDIDATES")
print("=" * 80)


# ============================================================
# ACTUAL ROUTE LENGTHS
# ============================================================

route_lengths = {
    "Route 1": 788.78495,
    "Route 2": 789.90222,
    "Route 3": 799.26005,
}


# ============================================================
# CREATE END CANDIDATES
# ============================================================

end_candidates = []

for route_name, route_length in route_lengths.items():

    route_data = candidates[
        candidates["route"] == route_name
    ].copy()

    if route_data.empty:
        print(
            f"WARNING: {route_name} not found."
        )
        continue

    # --------------------------------------------------------
    # Check whether an endpoint candidate already exists
    # --------------------------------------------------------

    existing_difference = (
        route_data["chainage_km"]
        - route_length
    ).abs()

    if existing_difference.min() < 0.001:

        print(
            f"{route_name}: endpoint already exists."
        )

        continue

    # --------------------------------------------------------
    # Find actual route-end coordinate
    # --------------------------------------------------------

    # The existing chainage layer contains the route's
    # final chainage point.
    last_point = route_data.loc[
        route_data["chainage_km"].idxmax()
    ]

    end_candidate = last_point.copy()

    end_candidate[
        "candidate_id"
    ] = (
        f"{route_name.replace(' ', '_')}_END"
    )

    end_candidate[
        "candidate_type"
    ] = "Route End Candidate"

    end_candidate[
        "chainage_m"
    ] = route_length * 1000

    end_candidate[
        "chainage_km"
    ] = route_length

    end_candidate[
        "distance_from_end_km"
    ] = 0.0

    end_candidate[
        "target_spacing_km"
    ] = 5.0

    end_candidate[
        "source_chainage_interval_km"
    ] = 1.0

    end_candidate[
        "target_chainage_error_km"
    ] = 0.0

    end_candidates.append(
        end_candidate
    )


# ============================================================
# COMBINE
# ============================================================

if end_candidates:

    end_gdf = gpd.GeoDataFrame(
        end_candidates,
        crs=candidates.crs
    )

    candidates = gpd.GeoDataFrame(
        pd.concat(
            [
                candidates,
                end_gdf
            ],
            ignore_index=True
        ),
        crs=candidates.crs
    )


# ============================================================
# SORT
# ============================================================

candidates = candidates.sort_values(
    [
        "route",
        "chainage_km"
    ]
).reset_index(
    drop=True
)


# ============================================================
# SAVE
# ============================================================

if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


candidates.to_file(
    OUTPUT_FILE,
    layer="station_candidates",
    driver="GPKG"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FINAL STATION CANDIDATE SUMMARY")
print("=" * 80)

summary = (
    candidates
    .groupby("route")
    .agg(
        candidates=(
            "candidate_id",
            "count"
        ),
        first_chainage_km=(
            "chainage_km",
            "min"
        ),
        last_chainage_km=(
            "chainage_km",
            "max"
        )
    )
    .reset_index()
)

print(
    summary.to_string(
        index=False
    )
)

print("\nTotal candidates:")
print(len(candidates))

print("\nOutput:")
print(OUTPUT_FILE)

print("\nCRS:")
print(candidates.crs)

print(
    "\nExact route-end candidates added successfully."
)