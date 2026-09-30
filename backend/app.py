from pathlib import Path

import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS


# ---------------------------------------------------------
# Application setup
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def load_csv(filename):
    path = RESULTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "HSR Alignment Intelligence API is running"
    })


# ---------------------------------------------------------
# Route comparison data
# ---------------------------------------------------------

@app.route("/api/routes")
def routes():

    df = load_csv("final_route_comparison.csv")

    return jsonify({
        "columns": df.columns.tolist(),
        "data": df.to_dict(orient="records")
    })


# ---------------------------------------------------------
# Final decision dataset
# ---------------------------------------------------------

@app.route("/api/decision")
def decision():

    df = load_csv("final_route_decision_dataset.csv")

    return jsonify({
        "columns": df.columns.tolist(),
        "data": df.to_dict(orient="records")
    })


# ---------------------------------------------------------
# Run server
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )