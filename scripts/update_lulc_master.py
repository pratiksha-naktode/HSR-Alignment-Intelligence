import pandas as pd
from pathlib import Path


# ============================================================
# HSR ROUTE OPTIMIZATION PROJECT
# UPDATE MASTER COMPARISON WITH VERIFIED LULC RESULTS
# ============================================================

BASE = Path(
    r"C:\Users\Texaxs\Desktop\hsr-route-optimization"
)

RESULTS = BASE / "data" / "results"


# ============================================================
# FILES
# ============================================================

MASTER_FILE = RESULTS / "route_comparison_raw.csv"

R1_LULC = RESULTS / "Route_1_lulc_summary_corrected.csv"
R2_LULC = RESULTS / "Route_2_lulc_summary.csv"
R3_LULC = RESULTS / "Route_3_lulc_summary.csv"


# ============================================================
# VERIFIED LULC VALUES
# ============================================================
#
# These values were calculated using:
#
# Permanent ground footprint = 3.5 m
# Half-width = 1.75 m
# CRS = EPSG:32643
#
# Do not use the old 2 m results.
# ============================================================

LULC_VALUES = {

    "Route 1": {
        "forest_area_km2": 0.04830729,
        "agriculture_area_km2": 0.87861230,
        "built_up_area_km2": 0.78187089,
    },

    "Route 2": {
        "forest_area_km2": 0.05549314,
        "agriculture_area_km2": 1.57102170,
        "built_up_area_km2": 0.73632199,
    },

    "Route 3": {
        "forest_area_km2": 0.05621451,
        "agriculture_area_km2": 1.53219794,
        "built_up_area_km2": 0.79308827,
    },
}


# ============================================================
# CHECK FILES
# ============================================================

if not MASTER_FILE.exists():

    raise FileNotFoundError(
        f"Master file not found:\n{MASTER_FILE}"
    )


for file_path in [
    R1_LULC,
    R2_LULC,
    R3_LULC,
]:

    if not file_path.exists():

        raise FileNotFoundError(
            f"LULC result not found:\n{file_path}"
        )


# ============================================================
# LOAD MASTER
# ============================================================

print("=" * 70)
print("UPDATING MASTER ROUTE COMPARISON")
print("=" * 70)

print("\nLoading master comparison...")

df = pd.read_csv(
    MASTER_FILE
)

print(
    f"Routes found: {len(df)}"
)

print(
    f"Columns found: {len(df.columns)}"
)


# ============================================================
# UPDATE C1-C3
# ============================================================

for route_name, values in LULC_VALUES.items():

    mask = (
        df["route"]
        .astype(str)
        .str.strip()
        .str.lower()
        == route_name.lower()
    )

    if not mask.any():

        raise ValueError(
            f"{route_name} not found in master CSV."
        )

    df.loc[
        mask,
        "forest_area_km2"
    ] = values[
        "forest_area_km2"
    ]

    df.loc[
        mask,
        "agriculture_area_km2"
    ] = values[
        "agriculture_area_km2"
    ]

    df.loc[
        mask,
        "built_up_area_km2"
    ] = values[
        "built_up_area_km2"
    ]


# ============================================================
# UPDATE LULC STATUS
# ============================================================

if "lulc_status" in df.columns:

    df["lulc_status"] = (
        "VERIFIED: 3.5m footprint + Bhuvan WMS"
    )


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    MASTER_FILE,
    index=False
)


# ============================================================
# VERIFY
# ============================================================

print("\n" + "=" * 70)
print("UPDATED MASTER LULC VALUES")
print("=" * 70)

columns = [
    "route",
    "forest_area_km2",
    "agriculture_area_km2",
    "built_up_area_km2",
]

print(
    df[columns].to_string(
        index=False
    )
)


# ============================================================
# CHECK MISSING VALUES
# ============================================================

lulc_columns = [
    "forest_area_km2",
    "agriculture_area_km2",
    "built_up_area_km2",
]

missing = df[
    lulc_columns
].isna().sum()


print("\n" + "=" * 70)
print("MISSING VALUE CHECK")
print("=" * 70)

print(missing)


if missing.sum() == 0:

    print(
        "\nC1, C2 and C3 are now populated for all routes."
    )

else:

    print(
        "\nWARNING: Some LULC values are still missing."
    )


print("\nMaster file updated:")
print(MASTER_FILE)

print("=" * 70)