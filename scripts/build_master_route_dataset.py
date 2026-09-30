import pandas as pd
import os

# ---------------------------------------------------------
# OUTPUT DIRECTORY
# ---------------------------------------------------------

os.makedirs("data/results", exist_ok=True)

# ---------------------------------------------------------
# VERIFIED ROUTE-LEVEL RESULTS
# 3.5 m permanent ground footprint
# ---------------------------------------------------------

data = [
    {
        "route": "R1",
        "forest_km2": 0.04830729,
        "agriculture_km2": 0.87861230,
        "builtup_km2": 0.78187089,
        "education_100m_count": 39,
        "wetland_km2": 0.02474273,
        "waterbody_direct_count": 0,
        "nearest_waterbody_km": 0.0069,
        "nearest_esz_km": 1.459039,
        "route_length_km": 788.785,
        "highway_interactions": 60,
    },
    {
        "route": "R2",
        "forest_km2": 0.05549314,
        "agriculture_km2": 1.57102170,
        "builtup_km2": 0.73632199,
        "education_100m_count": 31,
        "wetland_km2": 0.06322768,
        "waterbody_direct_count": 0,
        "nearest_waterbody_km": 0.0037,
        "nearest_esz_km": 3.398557,
        "route_length_km": 789.902,
        "highway_interactions": 55,
    },
    {
        "route": "R3",
        "forest_km2": 0.05621451,
        "agriculture_km2": 1.53219794,
        "builtup_km2": 0.79308827,
        "education_100m_count": 39,
        "wetland_km2": 0.04477389,
        "waterbody_direct_count": 0,
        "nearest_waterbody_km": 0.1885,
        "nearest_esz_km": 3.653662,
        "route_length_km": 799.260,
        "highway_interactions": 55,
    },
]

# ---------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------

df = pd.DataFrame(data)

# ---------------------------------------------------------
# ADD HIGHWAY BREAKDOWN
# ---------------------------------------------------------

df["nh_count"] = [52, 49, 47]

df["state_expressway_count"] = [5, 4, 5]

df["other_major_road_count"] = [3, 2, 3]

# MDR could not be identified from supplied dataset
df["mdr_count"] = None

# ---------------------------------------------------------
# ADD ESZ NAMES
# ---------------------------------------------------------

df["nearest_esz_name"] = [
    "Sanjay Gandhi National Park",
    "Kesu Bramahanand Reddy National Park",
    "Kesu Bramahanand Reddy National Park",
]

# ---------------------------------------------------------
# ADD NEAREST WATERBODY NAMES
# ---------------------------------------------------------

df["nearest_waterbody_name"] = [
    "Mohope",
    "DHULDEV Percolation Tank Desilting (Forest Comp. no.899 Pt)",
    "PT MAHASALVADI KAIKAD BARAMATI",
]

# ---------------------------------------------------------
# PROJECT ASSUMPTIONS
# ---------------------------------------------------------

df["ground_footprint_m"] = 3.5
df["buffer_each_side_m"] = 1.75
df["track_gauge_m"] = 1.435
df["planning_row_width_m"] = 17.5

# ---------------------------------------------------------
# SAVE MASTER DATASET
# ---------------------------------------------------------

output_file = (
    "data/results/master_route_analysis.csv"
)

df.to_csv(
    output_file,
    index=False
)

# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

print("\n================================")
print("MASTER ROUTE DATASET CREATED")
print("================================")

print(f"\nSaved: {output_file}")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nRoute summary:")
print(
    df[
        [
            "route",
            "forest_km2",
            "agriculture_km2",
            "builtup_km2",
            "education_100m_count",
            "wetland_km2",
            "waterbody_direct_count",
            "nearest_esz_km",
            "route_length_km",
            "highway_interactions",
        ]
    ].to_string(index=False)
)