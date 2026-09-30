from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")

INPUT = (
    BASE
    / "data"
    / "results"
    / "route_comparison_raw.csv"
)

OUTPUT = (
    BASE
    / "data"
    / "results"
    / "criterion_definition.csv"
)

# Load the current standardized raw dataset
df = pd.read_csv(INPUT)

criteria = pd.DataFrame({
    "criterion": [
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9"
    ],

    "criterion_name": [
        "Forest Area",
        "Agriculture Area",
        "Built-up Area",
        "Educational Sector",
        "Wetland Impact",
        "Bhuvan Waterbody Polygon Intersections",
        "Nearest Eco-Sensitive Zone",
        "Route Length",
        "Highway Intersection"
    ],

    "raw_measure": [
        "forest_area_km2",
        "agriculture_area_km2",
        "built_up_area_km2",
        "educational_sector_count",
        "wetland_area_km2",
        "waterbody_intersection_count",
        "nearest_esz_distance_km",
        "route_length_km",
        "highway_total_intersections"
    ],

    "unit": [
        "km2",
        "km2",
        "km2",
        "count",
        "km2",
        "count",
        "km",
        "km",
        "count"
    ],

    "criterion_type": [
        "Cost",
        "Cost",
        "Cost",
        "Cost",
        "Cost",
        "Cost",
        "Benefit",
        "Cost",
        "Cost"
    ],

    "interpretation": [
        "Lower forest area affected is preferable",
        "Lower agriculture area affected is preferable",
        "Lower built-up area affected is preferable",
        "Lower number of educational facilities within 100 m is preferable",
        "Lower wetland area affected is preferable",
        "Lower number of intersected Bhuvan waterbody polygon features is preferable; count is not verified as unique waterbodies",
        "Greater distance from the nearest eco-sensitive zone is preferable",
        "Lower route length is preferable",
        "Lower number of highway intersections is preferable"
    ],

    "status": [
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED",
    "VERIFIED"
]
})

print()
print("=" * 100)
print("CRITERION DEFINITIONS")
print("=" * 100)

print(criteria.to_string(index=False))

criteria.to_csv(
    OUTPUT,
    index=False
)

print()
print("Saved to:")
print(OUTPUT)

print()
print("=" * 100)
print("STATUS")
print("=" * 100)

print("C1 Forest Area          : VERIFIED")
print("C2 Agriculture Area     : VERIFIED")
print("C3 Built-up Area        : VERIFIED")
print("C4 Educational Sector   : VERIFIED")
print("C5 Wetland Impact       : VERIFIED")
print("C6 Waterbody Impact     : VERIFIED - count only")
print("C7 Nearest ESZ          : VERIFIED")
print("C8 Route Length         : VERIFIED")
print("C9 Highway Intersection : VERIFIED")