"""
app.py
------
Flask web application that serves a form for the 7 admission features
and returns a predicted "Chance of Admit" using the pre-trained
Linear Regression model (model/model.pkl + model/scaler.pkl).

Run with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
import pickle

import pandas as pd
from flask import Flask, render_template, request, jsonify

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(APP_DIR, "model")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load the trained model + scaler once, at startup (not on every request)
# ---------------------------------------------------------------------------
with open(os.path.join(MODEL_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)

with open(os.path.join(MODEL_DIR, "meta.pkl"), "rb") as f:
    meta = pickle.load(f)

FEATURE_COLUMNS = meta["features"]

# Sensible min/max bounds used both for basic validation and for rendering
# the sliders in the UI.
FIELD_SPECS = {
    "GRE Score": {"label": "GRE Score", "min": 260, "max": 340, "step": 1, "default": 320},
    "TOEFL Score": {"label": "TOEFL Score", "min": 0, "max": 120, "step": 1, "default": 110},
    "University Rating": {"label": "University Rating", "min": 1, "max": 5, "step": 1, "default": 3},
    "SOP": {"label": "Statement of Purpose (SOP) Strength", "min": 1, "max": 5, "step": 0.5, "default": 3.5},
    "LOR ": {"label": "Letter of Recommendation (LOR) Strength", "min": 1, "max": 5, "step": 0.5, "default": 3.5},
    "CGPA": {"label": "CGPA (out of 10)", "min": 0, "max": 10, "step": 0.01, "default": 8.5},
    "Research": {"label": "Research Experience", "min": 0, "max": 1, "step": 1, "default": 1},
}


def validate_and_extract(form_data):
    """Pulls the 7 required fields out of a dict-like object, validates
    them, and returns (values_list, errors_list) in FEATURE_COLUMNS order.
    """
    values = []
    errors = []

    for col in FEATURE_COLUMNS:
        spec = FIELD_SPECS[col]
        raw = form_data.get(col)

        if raw is None or str(raw).strip() == "":
            errors.append(f"{spec['label']} is required.")
            continue

        try:
            val = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{spec['label']} must be a number.")
            continue

        if val < spec["min"] or val > spec["max"]:
            errors.append(
                f"{spec['label']} must be between {spec['min']} and {spec['max']}."
            )
            continue

        values.append(val)

    return values, errors


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        fields=[{"name": col, **FIELD_SPECS[col]} for col in FEATURE_COLUMNS],
        meta=meta,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """Accepts either a normal form POST or a JSON POST and returns JSON."""
    payload = request.get_json(silent=True) or request.form

    values, errors = validate_and_extract(payload)

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    values_df = pd.DataFrame([values], columns=FEATURE_COLUMNS)
    scaled = scaler.transform(values_df)
    prediction = model.predict(scaled)[0]

    # Clamp to a sensible [0, 1] probability-like range for display
    prediction_clamped = max(0.0, min(1.0, prediction))

    return jsonify(
        {
            "success": True,
            "chance_of_admit": round(prediction_clamped * 100, 2),
            "raw_prediction": round(float(prediction), 4),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
