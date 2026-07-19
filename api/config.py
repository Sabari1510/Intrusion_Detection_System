"""Simple config for the IDS API."""

MODEL_PATH = "../models/stacking_ensemble.joblib"
MODEL_NAME = "SMOTE Stacking Ensemble"
DATASET = "CICIDS2017"
FEATURES = [
    "Fwd IAT Std", "Bwd IAT Min", "Flow IAT Min", "Bwd Packet Length Std",
    "Bwd Packet Length Mean", "Avg Bwd Segment Size", "Idle Min",
    "Bwd Packet Length Max", "Idle Mean", "Packet Length Std", "Idle Max",
    "Flow IAT Max", "Max Packet Length", "Fwd IAT Max", "Packet Length Variance",
    "Average Packet Size", "Packet Length Mean", "Active Min", "FIN Flag Count",
    "Active Std", "Flow IAT Std", "PSH Flag Count", "Active Mean", "Fwd IAT Total",
    "ACK Flag Count", "Flow Duration", "Bwd IAT Std", "Subflow Fwd Bytes",
    "Flow IAT Mean", "Min Packet Length",
]
CLASSES = ["BENIGN", "Bot", "DDoS", "DoS", "Brute Force", "PortScan", "Web Attack"]
