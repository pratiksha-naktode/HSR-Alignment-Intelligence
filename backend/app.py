from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


# ---------------------------------------------------------
# Application setup
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def load_csv(filename):
    path = RESULTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path)


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def frontend_files(path):
    file_path = FRONTEND_DIR / path

    if file_path.exists() and file_path.is_file():
        return send_from_directory(FRONTEND_DIR, path)

    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------
# GIS map
# ---------------------------------------------------------

@app.route("/data/results/<path:filename>")
def result_files(filename):
    return send_from_directory(RESULTS_DIR, filename)


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
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )