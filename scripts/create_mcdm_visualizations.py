import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE = Path(r"C:\Users\Texaxs\Desktop\hsr-route-optimization")
RESULTS = BASE / "data" / "results"

FINAL_FILE = RESULTS / "FINAL_HSR_ROUTE_RESULTS.csv"
WEIGHTS_FILE = RESULTS / "ahp_weights.csv"

OUTPUT_DIR = RESULTS / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

final_df = pd.read_csv(FINAL_FILE)
weights_df = pd.read_csv(WEIGHTS_FILE)

print("=" * 80)
print("CREATING MCDM VISUALIZATIONS")
print("=" * 80)


# ==================================================
# 1. FINAL ROUTE SCORE COMPARISON
# ==================================================

plt.figure(figsize=(9, 6))

plot_df = final_df.sort_values(
    "Final_Score",
    ascending=False
)

plt.bar(
    plot_df["route"],
    plot_df["Final_Score"]
)

plt.xlabel("Route")
plt.ylabel("Final MCDM Score")
plt.title("Final HSR Route Scores")

for i, value in enumerate(plot_df["Final_Score"]):
    plt.text(
        i,
        value + 0.01,
        f"{value:.4f}",
        ha="center"
    )

plt.ylim(0, 0.7)
plt.tight_layout()

score_file = OUTPUT_DIR / "final_route_scores.png"

plt.savefig(
    score_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print("1. Final route score chart:")
print(score_file)


# ==================================================
# 2. AHP WEIGHT DISTRIBUTION
# ==================================================

plt.figure(figsize=(9, 6))

plt.bar(
    weights_df["criterion"],
    weights_df["weight"]
)

plt.xlabel("Criterion")
plt.ylabel("AHP Weight")
plt.title("AHP Criterion Weights")

plt.xticks(
    rotation=20,
    ha="right"
)

for i, value in enumerate(weights_df["weight"]):
    plt.text(
        i,
        value + 0.01,
        f"{value:.2%}",
        ha="center"
    )

plt.ylim(0, 0.55)
plt.tight_layout()

weight_file = OUTPUT_DIR / "ahp_weights.png"

plt.savefig(
    weight_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print("2. AHP weight chart:")
print(weight_file)


# ==================================================
# 3. CRITERION CONTRIBUTION BY ROUTE
# ==================================================

contribution_columns = [
    "Highway_Contribution",
    "Waterbody_Contribution",
    "Wetland_Contribution",
    "ESZ_Contribution"
]

labels = [
    "Highway",
    "Waterbody",
    "Wetland",
    "ESZ"
]

plot_df = final_df.sort_values(
    "Final_Score",
    ascending=False
)

plt.figure(figsize=(10, 6))

bottom = [0] * len(plot_df)

for column, label in zip(
    contribution_columns,
    labels
):

    values = plot_df[column].values

    plt.bar(
        plot_df["route"],
        values,
        bottom=bottom,
        label=label
    )

    bottom = [
        bottom[i] + values[i]
        for i in range(len(values))
    ]

plt.xlabel("Route")
plt.ylabel("Weighted Contribution")
plt.title("Criterion Contributions to Final Route Scores")

plt.legend(
    title="Criteria"
)

plt.tight_layout()

contribution_file = (
    OUTPUT_DIR /
    "criterion_contributions.png"
)

plt.savefig(
    contribution_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print("3. Criterion contribution chart:")
print(contribution_file)


# ==================================================
# SUMMARY
# ==================================================

print()
print("=" * 80)
print("VISUALIZATION COMPLETE")
print("=" * 80)

print()
print("Files created:")

print(score_file)
print(weight_file)
print(contribution_file)