import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
SAROVAR = Path(r"C:\Users\Texaxs\Downloads\ROUTE_OPT\ctiteria_dataset\Amrit_Sarovar_Water_Observatory_Ponds.geojsonl")
RESULTS = BASE / "data" / "results"

RESULTS.mkdir(parents=True, exist_ok=True)

# Load Sarovar points
sarovar = gpd.read_file(SAROVAR)

print("Sarovar CRS:", sarovar.crs)
print("Total Sarovar features:", len(sarovar))
print("Geometry:", sarovar.geom_type.value_counts().to_dict())

# Reproject to same metric CRS as route corridors
sarovar = sarovar.to_crs("EPSG:32643")

summary = []
details = []

for route_no in [1, 2, 3]:

    corridor_path = BASE / "data" / "processed" / f"Route_{route_no}_corridor_2m.gpkg"

    corridor = gpd.read_file(corridor_path)

    # Find Sarovar points inside/intersecting the corridor
    matched = gpd.sjoin(
        sarovar,
        corridor[["geometry"]],
        how="inner",
        predicate="intersects"
    )

    # Remove duplicate matches if any
    matched = matched.drop_duplicates(subset=["Sarovar_ID"])

    summary.append({
        "route": f"Route {route_no}",
        "waterbody_count": len(matched)
    })

    if len(matched) > 0:
        matched["route"] = f"Route {route_no}"
        details.append(
            matched.drop(columns=["index_right"], errors="ignore")
        )

    print(f"Route {route_no}: {len(matched)} waterbodies")

summary_df = pd.DataFrame(summary)

summary_path = RESULTS / "waterbody_impact_summary.csv"
details_path = RESULTS / "waterbody_impact_details.csv"

summary_df.to_csv(summary_path, index=False)

if details:
    details_df = pd.concat(details, ignore_index=True)
    details_df.to_csv(details_path, index=False)
else:
    pd.DataFrame().to_csv(details_path, index=False)

print()
print("=== WATERBODY IMPACT SUMMARY ===")
print(summary_df.to_string(index=False))

print()
print("Summary saved to:", summary_path)
print("Details saved to:", details_path)
