import os
from pathlib import Path

# Paths
PROJECT_DIR = Path(r"A:\Network-Intrusion-Detection-System")
DATA_DIR = PROJECT_DIR / "dataset"
RAW_DATA_PATH = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
SELECTED_FEATURES_PATH = CLEANED_DATA_DIR / "selected_features.csv"
X_TRAIN_RESAMPLED_PATH = CLEANED_DATA_DIR / "X_train_resampled.csv"
Y_TRAIN_RESAMPLED_PATH = CLEANED_DATA_DIR / "y_train_resampled.csv"
X_TEST_PATH = CLEANED_DATA_DIR / "X_test.csv"
Y_TEST_PATH = CLEANED_DATA_DIR / "y_test.csv"

# Saved Models and Results
MODELS_DIR = PROJECT_DIR / "saved_models"
RESULTS_DIR = PROJECT_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

# Ensure directories exist
for d in [MODELS_DIR, FIGURES_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Data Preprocessing & Split Config
RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET_COLUMN = "Label"

# Resampling Strategy Constants (SMOTE + Undersampling)
# Target number of samples per class in training data after resampling
RESAMPLE_TARGET_SAMPLES = 100000

# Base Classifier Hyperparameters (RF tuned parameters, ET & LGBM tuning grids)
RF_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": RANDOM_STATE,
    "n_jobs": -1
}

# Grid for Extra Trees tuning
ET_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 15, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

# Grid for LightGBM tuning
LGBM_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [-1, 10, 20],
    "learning_rate": [0.01, 0.05, 0.1],
    "num_leaves": [31, 63, 127],
    "subsample": [0.7, 0.9, 1.0],
    "colsample_bytree": [0.7, 0.9, 1.0]
}

# Feature names (30 selected features)
SELECTED_FEATURES = [
    'Fwd IAT Std', 'Bwd IAT Min', 'Flow IAT Min', 'Bwd Packet Length Std', 
    'Bwd Packet Length Mean', 'Avg Bwd Segment Size', 'Idle Min', 'Bwd Packet Length Max', 
    'Idle Mean', 'Packet Length Std', 'Idle Max', 'Flow IAT Max', 
    'Max Packet Length', 'Fwd IAT Max', 'Packet Length Variance', 'Average Packet Size', 
    'Packet Length Mean', 'Active Min', 'FIN Flag Count', 'Active Std', 
    'Flow IAT Std', 'PSH Flag Count', 'Active Mean', 'Fwd IAT Total', 
    'ACK Flag Count', 'Flow Duration', 'Bwd IAT Std', 'Subflow Fwd Bytes', 
    'Flow IAT Mean', 'Min Packet Length'
]

# Standardized Label Map to clean up any unicode issues or formatting
LABEL_MAP = {
    'BENIGN': 'BENIGN',
    'DoS Hulk': 'DoS Hulk',
    'DDoS': 'DDoS',
    'PortScan': 'PortScan',
    'DoS GoldenEye': 'DoS GoldenEye',
    'FTP-Patator': 'FTP-Patator',
    'DoS slowloris': 'DoS slowloris',
    'DoS Slowhttptest': 'DoS Slowhttptest',
    'SSH-Patator': 'SSH-Patator',
    'Bot': 'Bot',
    'Web Attack \ufffd Brute Force': 'Web Attack - Brute Force',
    'Web Attack - Brute Force': 'Web Attack - Brute Force',
    'Web Attack \ufffd XSS': 'Web Attack - XSS',
    'Web Attack - XSS': 'Web Attack - XSS',
    'Infiltration': 'Infiltration',
    'Web Attack \ufffd Sql Injection': 'Web Attack - SQL Injection',
    'Web Attack - Sql Injection': 'Web Attack - SQL Injection',
    'Web Attack - SQL Injection': 'Web Attack - SQL Injection',
    'Heartbleed': 'Heartbleed'
}
