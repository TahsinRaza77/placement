"""
train_model.py
----------------
Trains a Linear Regression model to predict 'Chance of Admit' using the
Admission_Predict.csv dataset, then saves the fitted scaler and model to
disk (model/scaler.pkl, model/model.pkl) so the Flask app can load them
instantly without retraining on every request.

Run this once (or whenever the dataset changes):
    python train_model.py
"""

import os
import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error

DATA_PATH = "Admission_Predict.csv"
MODEL_DIR = "model"

FEATURE_COLUMNS = [
    "GRE Score",
    "TOEFL Score",
    "University Rating",
    "SOP",
    "LOR ",
    "CGPA",
    "Research",
]
TARGET_COLUMN = "Chance of Admit "


def train():
    os.makedirs(MODEL_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    # Basic cleaning (same intent as the original script)
    df["GRE Score"] = df["GRE Score"].fillna(df["GRE Score"].mean())
    df["TOEFL Score"] = df["TOEFL Score"].fillna(df["TOEFL Score"].mean())

    if "Serial No." in df.columns:
        df = df.drop(columns=["Serial No."])

    x = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    x_train, x_test, y_train, y_test = train_test_split(
        x_scaled, y, test_size=0.25, random_state=100
    )

    model = LinearRegression()
    model.fit(x_train, y_train)

    train_score = model.score(x_train, y_train)
    test_score = r2_score(y_test, model.predict(x_test))
    mae = mean_absolute_error(y_test, model.predict(x_test))

    print(f"Train R^2: {train_score:.4f}")
    print(f"Test  R^2: {test_score:.4f}")
    print(f"Test  MAE: {mae:.4f}")

    with open(os.path.join(MODEL_DIR, "model.pkl"), "wb") as f:
        pickle.dump(model, f)

    with open(os.path.join(MODEL_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    # Save feature order + simple metrics so the app can display/validate them
    meta = {
        "features": FEATURE_COLUMNS,
        "train_r2": train_score,
        "test_r2": test_score,
        "test_mae": mae,
    }
    with open(os.path.join(MODEL_DIR, "meta.pkl"), "wb") as f:
        pickle.dump(meta, f)

    print("Saved model.pkl, scaler.pkl and meta.pkl to the 'model/' folder.")


if __name__ == "__main__":
    train()
