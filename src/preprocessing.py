import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from pathlib import Path
from src.config import TARGET_COLUMN, LABEL_MAP, TEST_SIZE, RANDOM_STATE, RESAMPLE_TARGET_SAMPLES
from src.utils import setup_logger, timer_decorator

logger = setup_logger("preprocessing")

@timer_decorator(logger)
def load_and_clean_data(file_path: Path) -> pd.DataFrame:
    """Loads dataset and standardizes labels."""
    logger.info(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        logger.warning(f"Found {missing_count} missing values. Dropping rows...")
        df = df.dropna()
        
    # Check for infinite values and drop
    # (replace inf with nan and drop them)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    
    # Standardize and clean label names
    logger.info("Cleaning label names...")
    df[TARGET_COLUMN] = df[TARGET_COLUMN].map(LABEL_MAP)
    
    # If any labels were not mapped correctly, report and drop
    unmapped_count = df[TARGET_COLUMN].isnull().sum()
    if unmapped_count > 0:
        logger.warning(f"Found {unmapped_count} unmapped labels. Dropping rows...")
        df = df.dropna(subset=[TARGET_COLUMN])
        
    logger.info(f"Loaded dataset with shape {df.shape}")
    return df

@timer_decorator(logger)
def get_train_test_data(df: pd.DataFrame):
    """Performs stratified train-test split."""
    logger.info(f"Splitting dataset with test size {TEST_SIZE} and stratify...")
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    logger.info(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    return X_train, X_test, y_train, y_test

@timer_decorator(logger)
def apply_resampling(X_train: pd.DataFrame, y_train: pd.Series, target_samples: int = RESAMPLE_TARGET_SAMPLES):
    """
    Applies hybrid SMOTE oversampling and Random Undersampling to balance the dataset.
    
    - Oversamples minority classes (< target_samples) to target_samples using SMOTE.
    - Undersamples majority classes (> target_samples) to target_samples using RandomUnderSampler.
    """
    logger.info(f"Applying hybrid resampling. Target samples per class: {target_samples}")
    
    # Count samples in each class
    class_counts = y_train.value_counts().to_dict()
    logger.info(f"Original training class distribution:\n{y_train.value_counts()}")
    
    # 1. Setup Oversampling strategy for minority classes
    oversample_strategy = {}
    min_class_size = 999999
    
    for cls, count in class_counts.items():
        if count < target_samples:
            oversample_strategy[cls] = target_samples
        if count < min_class_size:
            min_class_size = count
            
    logger.info(f"Classes to oversample: {list(oversample_strategy.keys())}")
    
    # Apply SMOTE if there are minority classes to oversample
    if oversample_strategy:
        # Determine safe k_neighbors (min class size - 1, capped at 5)
        # If min class size is extremely small (e.g. Heartbleed has ~8 samples in train),
        # k_neighbors must be less than that size.
        k_neighbors = min(5, max(1, min_class_size - 1))
        logger.info(f"Running SMOTE with k_neighbors={k_neighbors}...")
        
        smote = SMOTE(
            sampling_strategy=oversample_strategy,
            k_neighbors=k_neighbors,
            random_state=RANDOM_STATE
        )
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        logger.info(f"After SMOTE, training set shape: {X_train_res.shape}")
    else:
        X_train_res, y_train_res = X_train, y_train
        
    # 2. Setup Undersampling strategy for majority classes
    # Re-evaluate class counts after SMOTE
    class_counts_res = y_train_res.value_counts().to_dict()
    undersample_strategy = {}
    
    for cls, count in class_counts_res.items():
        if count > target_samples:
            undersample_strategy[cls] = target_samples
            
    logger.info(f"Classes to undersample: {list(undersample_strategy.keys())}")
    
    # Apply RandomUnderSampler if there are majority classes to undersample
    if undersample_strategy:
        logger.info("Running RandomUnderSampler...")
        rus = RandomUnderSampler(
            sampling_strategy=undersample_strategy,
            random_state=RANDOM_STATE
        )
        X_train_final, y_train_final = rus.fit_resample(X_train_res, y_train_res)
        logger.info(f"After Undersampling, training set shape: {X_train_final.shape}")
    else:
        X_train_final, y_train_final = X_train_res, y_train_res
        
    logger.info(f"Balanced training class distribution:\n{y_train_final.value_counts()}")
    return X_train_final, y_train_final
