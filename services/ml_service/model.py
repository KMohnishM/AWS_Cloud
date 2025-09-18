from flask import Flask, request, jsonify
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
import joblib
import os

app = Flask(__name__)

MODEL_FILENAME = "iforest_model.pkl"

# Full feature list including fio2
feature_names = [
    "heart_rate", "bp_systolic", "bp_diastolic", "respiratory_rate",
    "spo2", "etco2", "fio2", "temperature", "wbc_count", "lactate", "blood_glucose"
]

# Function to train and save the model
def train_model():
    np.random.seed(42)
    data = pd.DataFrame({
        "heart_rate": np.random.normal(75, 10, 300),
        "bp_systolic": np.random.normal(120, 15, 300),
        "bp_diastolic": np.random.normal(80, 10, 300),
        "respiratory_rate": np.random.normal(18, 3, 300),
        "spo2": np.random.normal(97, 2, 300),
        "etco2": np.random.normal(37, 4, 300),
        "fio2": np.random.normal(21, 2, 300),  # Normal room air is ~21%
        "temperature": np.random.normal(36.6, 0.5, 300),
        "wbc_count": np.random.normal(7, 1.5, 300),
        "lactate": np.random.normal(1.2, 0.4, 300),
        "blood_glucose": np.random.normal(95, 15, 300),
    })
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(data)
    joblib.dump(model, MODEL_FILENAME)

# Load or train model
if not os.path.exists(MODEL_FILENAME):
    train_model()
model = joblib.load(MODEL_FILENAME)

# Predict route
@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.json

    try:
        features = [input_data[feat] for feat in feature_names]
    except KeyError as e:
        return jsonify({"error": f"Missing feature in input: {str(e)}"}), 400

    X = pd.DataFrame([features], columns=feature_names)

    score = model.decision_function(X)[0]
    anomaly_score = 1 - score

    return jsonify({"anomaly_score": round(anomaly_score, 4)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)