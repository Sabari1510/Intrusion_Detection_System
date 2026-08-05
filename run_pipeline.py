import argparse
import json
import time
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

from src.config import (
    SELECTED_FEATURES_PATH,
    ET_PARAM_GRID,
    LGBM_PARAM_GRID,
    REPORTS_DIR,
    RESAMPLE_TARGET_SAMPLES,
    RANDOM_STATE
)
from src.utils import setup_logger, timer_decorator
from src.preprocessing import load_and_clean_data, get_train_test_data, apply_resampling
from src.model_training import (
    tune_hyperparameters,
    train_base_models,
    train_stacking_ensemble,
    save_model
)
from src.evaluation import evaluate_model, plot_confusion_matrix, save_comparison_report

logger = setup_logger("run_pipeline", REPORTS_DIR / "pipeline_run.log")

@timer_decorator(logger)
def main():
    parser = argparse.ArgumentParser(description="CICIDS2017 Stacking NIDS Pipeline")
    parser.add_argument("--mode", type=str, default="full", choices=["full", "tune_only", "train_only", "dry_run"],
                        help="Pipeline run mode: full, tune_only, train_only, or dry_run")
    parser.add_argument("--tune-size", type=int, default=30000,
                        help="Number of samples to extract for hyperparameter tuning subset")
    parser.add_argument("--tune-iter", type=int, default=5,
                        help="Number of iterations for RandomizedSearchCV tuning")
    parser.add_argument("--meta-learner", type=str, default="logistic", choices=["logistic", "xgboost"],
                        help="Meta-learner classifier for Stacking Ensemble")
    args = parser.parse_args()
    
    logger.info(f"=== Starting NIDS Pipeline (Mode: {args.mode}) ===")
    
    # 1. Load and clean dataset
    df = load_and_clean_data(SELECTED_FEATURES_PATH)
    
    # 2. Train-Test Split (stratified)
    X_train, X_test, y_train, y_test = get_train_test_data(df)
    
    # Cache file path for best parameters
    params_file = REPORTS_DIR / "best_params.json"
    best_params = {"et": None, "lgbm": None}
    
    # Load cached parameters if available
    if params_file.exists() and args.mode != "tune_only":
        try:
            with open(params_file, "r") as f:
                best_params = json.load(f)
            logger.info(f"Loaded cached hyperparameters from {params_file}")
        except Exception as e:
            logger.warning(f"Error loading cached parameters: {e}. Will use defaults.")
            
    # 3. Hyperparameter Tuning Phase (if required)
    if args.mode in ["full", "tune_only"] and not (params_file.exists() and args.mode == "full"):
        logger.info(f"Executing Hyperparameter Tuning (using subset of size {args.tune_size})...")
        
        # Extract a stratified subset for tuning to speed up RandomizedSearchCV
        # Ensure we don't request more than available training samples
        tune_subset_size = min(args.tune_size, len(X_train) - 100)
        
        X_train_sub, _, y_train_sub, _ = train_test_split(
            X_train, y_train,
            train_size=tune_subset_size,
            stratify=y_train,
            random_state=RANDOM_STATE
        )
        
        # Apply SMOTE to the tuning subset to balance classes
        # Target 2000 samples per class for quick tuning
        X_train_sub_res, y_train_sub_res = apply_resampling(X_train_sub, y_train_sub, target_samples=3000)
        
        # Run tuning
        best_params_et = tune_hyperparameters("et", X_train_sub_res, y_train_sub_res, ET_PARAM_GRID, n_iter=args.tune_iter)
        best_params_lgbm = tune_hyperparameters("lgbm", X_train_sub_res, y_train_sub_res, LGBM_PARAM_GRID, n_iter=args.tune_iter)
        
        best_params = {"et": best_params_et, "lgbm": best_params_lgbm}
        
        # Cache hyperparameters
        with open(params_file, "w") as f:
            json.dump(best_params, f, indent=4)
        logger.info(f"Saved optimized hyperparameters to {params_file}")
        
        if args.mode == "tune_only":
            logger.info("Tuning phase complete. Exiting.")
            return

    # 4. Dry Run Mode (Fast test of execution flow)
    if args.mode == "dry_run":
        logger.info("Executing Dry Run...")
        # Train on a tiny balanced subset of 5,000 samples per class
        X_train_final, y_train_final = apply_resampling(X_train, y_train, target_samples=5000)
        
        base_models = train_base_models(X_train_final, y_train_final, best_params["et"], best_params["lgbm"])
        
        stacking_model = train_stacking_ensemble(
            X_train_final, y_train_final, 
            best_params_et=best_params["et"],
            best_params_lgbm=best_params["lgbm"],
            meta_learner_type=args.meta_learner
        )
        
        # Test predictions
        y_pred = stacking_model.predict(X_test.head(1000))
        logger.info("Dry Run Completed Successfully.")
        return

    # 5. Full Pipeline Training
    # Apply full resampling on training dataset
    X_train_final, y_train_final = apply_resampling(X_train, y_train, RESAMPLE_TARGET_SAMPLES)
    
    # Train base models
    base_models = train_base_models(X_train_final, y_train_final, best_params["et"], best_params["lgbm"])
    
    # Train Stacking Ensemble Classifier
    stacking_model = train_stacking_ensemble(
        X_train_final, y_train_final,
        best_params_et=best_params["et"],
        best_params_lgbm=best_params["lgbm"],
        meta_learner_type=args.meta_learner
    )
    
    # Save Models
    save_model(base_models["rf"], "rf_model.joblib")
    save_model(base_models["et"], "et_model.joblib")
    save_model(base_models["lgbm"], "lgbm_model.joblib")
    save_model(stacking_model, "stacking_ensemble_model.joblib")
    
    # 6. Evaluation Phase
    logger.info("Evaluating all trained models on test dataset...")
    results = []
    
    # Evaluate individual base models
    for name, model in base_models.items():
        y_pred = model.predict(X_test)
        metrics = evaluate_model(y_test, y_pred, f"{name.upper()} Model")
        plot_confusion_matrix(y_test, y_pred, f"{name.upper()} Model")
        results.append(metrics)
        
    # Evaluate Stacking Ensemble
    y_pred_stack = stacking_model.predict(X_test)
    metrics_stack = evaluate_model(y_test, y_pred_stack, "Stacking Ensemble")
    plot_confusion_matrix(y_test, y_pred_stack, "Stacking Ensemble")
    results.append(metrics_stack)
    
    # Save comparison reports
    save_comparison_report(results, "model_comparison.csv")
    
    logger.info("=== NIDS Pipeline Execution Completed Successfully ===")

if __name__ == "__main__":
    main()
