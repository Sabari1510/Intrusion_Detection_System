import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from src.config import FIGURES_DIR, REPORTS_DIR
from src.utils import setup_logger

logger = setup_logger("evaluation")

def evaluate_model(y_test, y_pred, model_name: str) -> dict:
    """Calculates accuracy, precision, recall, and F1 score for predictions."""
    logger.info(f"Evaluating metrics for {model_name}...")
    
    accuracy = accuracy_score(y_test, y_pred)
    # Use average='weighted' to account for class distribution
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    
    logger.info(f"[{model_name}] Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    report_text = classification_report(y_test, y_pred, zero_division=0)
    
    # Save text report
    report_file = REPORTS_DIR / f"{model_name.lower().replace(' ', '_')}_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    logger.info(f"Saved text classification report to {report_file}")
    
    return {
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "report_dict": report_dict
    }

def plot_confusion_matrix(y_test, y_pred, model_name: str):
    """Generates and saves a confusion matrix heatmap for the model."""
    logger.info(f"Generating confusion matrix for {model_name}...")
    
    # Get unique classes present in y_test
    classes = sorted(list(np.unique(y_test)))
    
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    
    # Normalize confusion matrix
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm) # Replace NaNs with 0
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm_norm,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes
    )
    plt.title(f"Normalized Confusion Matrix - {model_name}")
    plt.ylabel("Actual Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    file_name = f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"
    save_path = FIGURES_DIR / file_name
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved confusion matrix plot to {save_path}")
    return save_path

def save_comparison_report(results: list, file_name: str = "model_comparison.csv"):
    """Compiles evaluation metrics from multiple models and saves a comparison table."""
    comparison_data = []
    for r in results:
        comparison_data.append({
            "Model": r["model"],
            "Accuracy": r["accuracy"],
            "Precision": r["precision"],
            "Recall": r["recall"],
            "F1-Score": r["f1_score"]
        })
        
    df = pd.DataFrame(comparison_data)
    save_path = REPORTS_DIR / file_name
    df.to_csv(save_path, index=False)
    logger.info(f"Saved comparison report to {save_path}")
    
    # Also save as JSON for backend use if needed
    json_path = REPORTS_DIR / "model_comparison.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=4)
        
    return df
