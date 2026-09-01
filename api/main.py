import os
import sys
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

# Add project root to python path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import MODELS_DIR, SELECTED_FEATURES

app = FastAPI(
    title="NIDS Stacking Ensemble API",
    description="REST API for predicting network intrusions using a SMOTE-Enhanced Stacking Ensemble model.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded models
model = None
classes = []

# Model path
MODEL_PATH = MODELS_DIR / "stacking_ensemble_model.joblib"

class NetworkFlowInput(BaseModel):
    fwd_iat_std: float = Field(..., alias='Fwd IAT Std')
    bwd_iat_min: float = Field(..., alias='Bwd IAT Min')
    flow_iat_min: float = Field(..., alias='Flow IAT Min')
    bwd_packet_length_std: float = Field(..., alias='Bwd Packet Length Std')
    bwd_packet_length_mean: float = Field(..., alias='Bwd Packet Length Mean')
    avg_bwd_segment_size: float = Field(..., alias='Avg Bwd Segment Size')
    idle_min: float = Field(..., alias='Idle Min')
    bwd_packet_length_max: float = Field(..., alias='Bwd Packet Length Max')
    idle_mean: float = Field(..., alias='Idle Mean')
    packet_length_std: float = Field(..., alias='Packet Length Std')
    idle_max: float = Field(..., alias='Idle Max')
    flow_iat_max: float = Field(..., alias='Flow IAT Max')
    max_packet_length: float = Field(..., alias='Max Packet Length')
    fwd_iat_max: float = Field(..., alias='Fwd IAT Max')
    packet_length_variance: float = Field(..., alias='Packet Length Variance')
    average_packet_size: float = Field(..., alias='Average Packet Size')
    packet_length_mean: float = Field(..., alias='Packet Length Mean')
    active_min: float = Field(..., alias='Active Min')
    fin_flag_count: int = Field(..., alias='FIN Flag Count')
    active_std: float = Field(..., alias='Active Std')
    flow_iat_std: float = Field(..., alias='Flow IAT Std')
    psh_flag_count: int = Field(..., alias='PSH Flag Count')
    active_mean: float = Field(..., alias='Active Mean')
    fwd_iat_total: float = Field(..., alias='Fwd IAT Total')
    ack_flag_count: int = Field(..., alias='ACK Flag Count')
    flow_duration: float = Field(..., alias='Flow Duration')
    bwd_iat_std: float = Field(..., alias='Bwd IAT Std')
    subflow_fwd_bytes: float = Field(..., alias='Subflow Fwd Bytes')
    flow_iat_mean: float = Field(..., alias='Flow IAT Mean')
    min_packet_length: float = Field(..., alias='Min Packet Length')

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Fwd IAT Std": 0.0,
                "Bwd IAT Min": 0.0,
                "Flow IAT Min": 4.0,
                "Bwd Packet Length Std": 0.0,
                "Bwd Packet Length Mean": 0.0,
                "Avg Bwd Segment Size": 0.0,
                "Idle Min": 0.0,
                "Bwd Packet Length Max": 0.0,
                "Idle Mean": 0.0,
                "Packet Length Std": 0.0,
                "Idle Max": 0.0,
                "Flow IAT Max": 4.0,
                "Max Packet Length": 6.0,
                "Fwd IAT Max": 0.0,
                "Packet Length Variance": 0.0,
                "Average Packet Size": 9.0,
                "Packet Length Mean": 6.0,
                "Active Min": 0.0,
                "FIN Flag Count": 0,
                "Active Std": 0.0,
                "Flow IAT Std": 0.0,
                "PSH Flag Count": 0,
                "Active Mean": 0.0,
                "Fwd IAT Total": 0.0,
                "ACK Flag Count": 1,
                "Flow Duration": 4.0,
                "Bwd IAT Std": 0.0,
                "Subflow Fwd Bytes": 6.0,
                "Flow IAT Mean": 4.0,
                "Min Packet Length": 6.0
            }
        }

@app.on_event("startup")
def load_trained_model():
    global model, classes
    print(f"Checking model at: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        # Load one of the dry run base models if full model doesn't exist yet, for API testing
        dry_run_path = MODELS_DIR / "rf_model.joblib"
        if dry_run_path.exists():
            print("Ensemble not found. Loading test Random Forest model instead...")
            model = joblib.load(dry_run_path)
            classes = list(model.classes_)
        else:
            print("WARNING: No pre-trained model found. Endpoints will fail until model is trained.")
            model = None
            classes = []
    else:
        print("Loading Stacking Ensemble model...")
        model = joblib.load(MODEL_PATH)
        classes = list(model.classes_)
        print(f"Stacking Ensemble model loaded. Target Classes: {classes}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "model_loaded": model is not None,
        "classes": classes,
        "message": "Welcome to the SMOTE-Enhanced Stacking Ensemble NIDS API"
    }

@app.post("/predict")
def predict_flow(flow_input: NetworkFlowInput):
    global model, classes
    if model is None:
        # Try loading model on demand in case it was trained after startup
        if MODEL_PATH.exists():
            load_trained_model()
        else:
            raise HTTPException(status_code=503, detail="Model not loaded or trained yet.")
            
    try:
        # Convert request body to Pandas DataFrame with correct ordering
        data_dict = flow_input.model_dump(by_alias=True)
        # Reorder to match configuration selected features exactly
        ordered_data = {feat: [data_dict[feat]] for feat in SELECTED_FEATURES}
        df = pd.DataFrame(ordered_data)
        
        # Run prediction
        prediction = model.predict(df)[0]
        
        # Run class probability distribution (confidence scores)
        probabilities = model.predict_proba(df)[0]
        prob_dict = {classes[i]: float(probabilities[i]) for i in range(len(classes))}
        
        # Severity ranking for dashboard
        severity = "info"
        if prediction == "BENIGN":
            severity = "success"
        elif prediction in ["PortScan", "FTP-Patator", "SSH-Patator", "Web Attack - Brute Force", "Web Attack - XSS"]:
            severity = "warning"
        elif prediction in ["DoS Hulk", "DDoS", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest", "Bot", "Infiltration", "Web Attack - SQL Injection", "Heartbleed"]:
            severity = "danger"
            
        return {
            "prediction": prediction,
            "confidence": float(prob_dict[prediction]),
            "severity": severity,
            "probabilities": prob_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/presets")
def get_presets():
    """Returns realistic mock samples representing various traffic classes to easily load on frontend."""
    return {
        "BENIGN": {
            "Fwd IAT Std": 0.0,
            "Bwd IAT Min": 0.0,
            "Flow IAT Min": 4.0,
            "Bwd Packet Length Std": 0.0,
            "Bwd Packet Length Mean": 0.0,
            "Avg Bwd Segment Size": 0.0,
            "Idle Min": 0.0,
            "Bwd Packet Length Max": 0.0,
            "Idle Mean": 0.0,
            "Packet Length Std": 0.0,
            "Idle Max": 0.0,
            "Flow IAT Max": 4.0,
            "Max Packet Length": 6.0,
            "Fwd IAT Max": 0.0,
            "Packet Length Variance": 0.0,
            "Average Packet Size": 9.0,
            "Packet Length Mean": 6.0,
            "Active Min": 0.0,
            "FIN Flag Count": 0,
            "Active Std": 0.0,
            "Flow IAT Std": 0.0,
            "PSH Flag Count": 0,
            "Active Mean": 0.0,
            "Fwd IAT Total": 0.0,
            "ACK Flag Count": 1,
            "Flow Duration": 4.0,
            "Bwd IAT Std": 0.0,
            "Subflow Fwd Bytes": 6.0,
            "Flow IAT Mean": 4.0,
            "Min Packet Length": 6.0
        },
        "DDoS": {
            "Fwd IAT Std": 38.67,
            "Bwd IAT Min": 2.0,
            "Flow IAT Min": 1.0,
            "Bwd Packet Length Std": 128.5,
            "Bwd Packet Length Mean": 110.0,
            "Avg Bwd Segment Size": 110.0,
            "Idle Min": 0.0,
            "Bwd Packet Length Max": 350.0,
            "Idle Mean": 0.0,
            "Packet Length Std": 182.2,
            "Idle Max": 0.0,
            "Flow IAT Max": 2400.0,
            "Max Packet Length": 350.0,
            "Fwd IAT Max": 2300.0,
            "Packet Length Variance": 33200.0,
            "Average Packet Size": 95.0,
            "Packet Length Mean": 85.0,
            "Active Min": 0.0,
            "FIN Flag Count": 0,
            "Active Std": 0.0,
            "Flow IAT Std": 312.4,
            "PSH Flag Count": 1,
            "Active Mean": 0.0,
            "Fwd IAT Total": 4800.0,
            "ACK Flag Count": 0,
            "Flow Duration": 4900.0,
            "Bwd IAT Std": 14.5,
            "Subflow Fwd Bytes": 120.0,
            "Flow IAT Mean": 160.0,
            "Min Packet Length": 0.0
        },
        "PortScan": {
            "Fwd IAT Std": 0.0,
            "Bwd IAT Min": 0.0,
            "Flow IAT Min": 1.0,
            "Bwd Packet Length Std": 0.0,
            "Bwd Packet Length Mean": 0.0,
            "Avg Bwd Segment Size": 0.0,
            "Idle Min": 0.0,
            "Bwd Packet Length Max": 0.0,
            "Idle Mean": 0.0,
            "Packet Length Std": 0.0,
            "Idle Max": 0.0,
            "Flow IAT Max": 1.0,
            "Max Packet Length": 0.0,
            "Fwd IAT Max": 0.0,
            "Packet Length Variance": 0.0,
            "Average Packet Size": 0.0,
            "Packet Length Mean": 0.0,
            "Active Min": 0.0,
            "FIN Flag Count": 0,
            "Active Std": 0.0,
            "Flow IAT Std": 0.0,
            "PSH Flag Count": 0,
            "Active Mean": 0.0,
            "Fwd IAT Total": 0.0,
            "ACK Flag Count": 1,
            "Flow Duration": 1.0,
            "Bwd IAT Std": 0.0,
            "Subflow Fwd Bytes": 0.0,
            "Flow IAT Mean": 1.0,
            "Min Packet Length": 0.0
        },
        "Botnet": {
            "Fwd IAT Std": 124312.0,
            "Bwd IAT Min": 23.0,
            "Flow IAT Min": 2.0,
            "Bwd Packet Length Std": 456.2,
            "Bwd Packet Length Mean": 320.0,
            "Avg Bwd Segment Size": 320.0,
            "Idle Min": 4500000.0,
            "Bwd Packet Length Max": 1024.0,
            "Idle Mean": 5000000.0,
            "Packet Length Std": 395.0,
            "Idle Max": 5500000.0,
            "Flow IAT Max": 500000.0,
            "Max Packet Length": 1024.0,
            "Fwd IAT Max": 480000.0,
            "Packet Length Variance": 156000.0,
            "Average Packet Size": 210.0,
            "Packet Length Mean": 180.0,
            "Active Min": 23000.0,
            "Active Std": 0.0,
            "Flow IAT Std": 94300.0,
            "PSH Flag Count": 1,
            "Active Mean": 23000.0,
            "Fwd IAT Total": 2400000.0,
            "ACK Flag Count": 0,
            "Flow Duration": 12000000.0,
            "Bwd IAT Std": 12040.0,
            "Subflow Fwd Bytes": 500.0,
            "Flow IAT Mean": 43500.0,
            "Min Packet Length": 0.0
        }
    }
