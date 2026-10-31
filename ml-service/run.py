"""
Flask Machine Learning Microservice Entry Point
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
PES Institute of Technology and Management, Shivamogga - VTU
"""

import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv("PORT", 5001))


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint consumed by Express backend and monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "CAMPS-ML XGBoost Inference Service",
        "port": PORT,
        "environment": os.getenv("FLASK_ENV", "development"),
        "version": os.getenv("MODEL_VERSION", "v1.0.0"),
        "institution": "PESITM Shivamogga (VTU)"
    }), 200


@app.route("/model/info", methods=["GET"])
def model_info():
    """Returns metadata about the active ML model."""
    return jsonify({
        "model_name": "XGBoost Student Academic Risk Classifier + TreeSHAP",
        "version": os.getenv("MODEL_VERSION", "v1.0.0"),
        "algorithm": "Extreme Gradient Boosting (XGBoost)",
        "features": [
            "attendance_percentage",
            "avg_internal_marks",
            "avg_assignment_score",
            "previous_gpa",
            "participation_score"
        ],
        "risk_tiers": {
            "low": "< 0.35 failure probability",
            "medium": "0.35 to 0.60 failure probability",
            "high": ">= 0.60 failure probability"
        }
    }), 200


if __name__ == "__main__":
    print("=" * 65)
    print(f"[+] CAMPS-ML Flask Microservice starting on http://127.0.0.1:{PORT}")
    print("=" * 65)
    app.run(host="127.0.0.1", port=PORT, debug=True)
