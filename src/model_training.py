import joblib
from pathlib import Path
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from src.config import RANDOM_STATE, RF_PARAMS, MODELS_DIR
from src.utils import setup_logger, timer_decorator

logger = setup_logger("model_training")

@timer_decorator(logger)
def tune_hyperparameters(model_type: str, X_train_sub, y_train_sub, param_grid: dict, n_iter: int = 10) -> dict:
    """Runs RandomizedSearchCV to find the best hyperparameters for ET or LightGBM on a subset."""
    logger.info(f"Tuning hyperparameters for '{model_type}' on a subset of shape {X_train_sub.shape} with {n_iter} iterations...")
    
    if model_type == "et":
        base_model = ExtraTreesClassifier(random_state=RANDOM_STATE, n_jobs=-1)
    elif model_type == "lgbm":
        base_model = LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1)
    else:
        raise ValueError(f"Unknown model type for tuning: {model_type}")
        
    cv = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=n_iter,
        cv=3,
        scoring="f1_weighted",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )
    
    cv.fit(X_train_sub, y_train_sub)
    logger.info(f"Best parameters found for '{model_type}': {cv.best_params_}")
    logger.info(f"Best cross-validation F1 score: {cv.best_score_:.4f}")
    
    return cv.best_params_

@timer_decorator(logger)
def train_base_models(X_train, y_train, best_params_et=None, best_params_lgbm=None) -> dict:
    """Trains the individual base models on the training dataset."""
    logger.info("Initializing and training base classifiers on the balanced training data...")
    
    # 1. Random Forest (pre-tuned parameters)
    logger.info("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(**RF_PARAMS)
    rf_model.fit(X_train, y_train)
    logger.info("Random Forest training completed.")
    
    # 2. Extra Trees
    et_params = {"random_state": RANDOM_STATE, "n_jobs": -1}
    if best_params_et:
        et_params.update(best_params_et)
    logger.info(f"Training Extra Trees Classifier with parameters: {et_params}...")
    et_model = ExtraTreesClassifier(**et_params)
    et_model.fit(X_train, y_train)
    logger.info("Extra Trees training completed.")
    
    # 3. LightGBM
    lgbm_params = {"random_state": RANDOM_STATE, "n_jobs": -1, "verbosity": -1}
    if best_params_lgbm:
        lgbm_params.update(best_params_lgbm)
    logger.info(f"Training LightGBM Classifier with parameters: {lgbm_params}...")
    lgbm_model = LGBMClassifier(**lgbm_params)
    lgbm_model.fit(X_train, y_train)
    logger.info("LightGBM training completed.")
    
    return {
        "rf": rf_model,
        "et": et_model,
        "lgbm": lgbm_model
    }

@timer_decorator(logger)
def train_stacking_ensemble(X_train, y_train, best_params_et=None, best_params_lgbm=None, meta_learner_type: str = "logistic"):
    """
    Fits a StackingClassifier using Random Forest, Extra Trees, and LightGBM base models,
    with either Logistic Regression or XGBoost as the meta-learner.
    """
    logger.info(f"Configuring Stacking Ensemble with meta-learner: {meta_learner_type}...")
    
    # Define base estimators
    rf_est = RandomForestClassifier(**RF_PARAMS)
    
    et_params = {"random_state": RANDOM_STATE, "n_jobs": -1}
    if best_params_et:
        et_params.update(best_params_et)
    et_est = ExtraTreesClassifier(**et_params)
    
    lgbm_params = {"random_state": RANDOM_STATE, "n_jobs": -1, "verbosity": -1}
    if best_params_lgbm:
        lgbm_params.update(best_params_lgbm)
    lgbm_est = LGBMClassifier(**lgbm_params)
    
    estimators = [
        ("rf", rf_est),
        ("et", et_est),
        ("lgbm", lgbm_est)
    ]
    
    # Define meta-learner
    if meta_learner_type == "logistic":
        meta_learner = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, n_jobs=-1)
    elif meta_learner_type == "xgboost":
        meta_learner = XGBClassifier(n_estimators=100, random_state=RANDOM_STATE, eval_metric="mlogloss", n_jobs=-1)
    else:
        raise ValueError(f"Unknown meta-learner type: {meta_learner_type}")
        
    stacking_clf = StackingClassifier(
        estimators=estimators,
        final_estimator=meta_learner,
        n_jobs=-1,
        cv=3  # 3-fold CV for generating out-of-fold predictions for meta-learner training
    )
    
    logger.info("Training Stacking Classifier (this will train base estimators and meta-learner)...")
    stacking_clf.fit(X_train, y_train)
    logger.info("Stacking Ensemble training completed.")
    
    return stacking_clf

def save_model(model, file_name: str):
    """Saves a model to the models folder."""
    file_path = MODELS_DIR / file_name
    logger.info(f"Saving model to {file_path}...")
    joblib.dump(model, file_path)
    logger.info("Model saved successfully.")
    return file_path

def load_model(file_name: str):
    """Loads a model from the models folder."""
    file_path = MODELS_DIR / file_name
    logger.info(f"Loading model from {file_path}...")
    if not file_path.exists():
        raise FileNotFoundError(f"Model file not found: {file_path}")
    model = joblib.load(file_path)
    logger.info("Model loaded successfully.")
    return model
