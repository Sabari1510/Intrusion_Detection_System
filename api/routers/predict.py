"""Prediction routes."""

from fastapi import APIRouter, File, UploadFile, HTTPException

from config import MODEL_NAME, DATASET, FEATURES, CLASSES, MODEL_PATH
from schemas.prediction import PredictionRequest, PredictionResponse
from services.model_service import model_service
from utils.helper import rows_from_csv

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    """Predict attack class for one network flow."""
    try:
        label, conf = model_service.predict(data.features)
        return PredictionResponse(
            predicted_class=label,
            confidence=conf,
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch_predict")
async def batch_predict(file: UploadFile = File(...)):
    """Predict for each row in a CSV file."""
    content = await file.read()
    try:
        rows = rows_from_csv(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad CSV: {e}")

    results = []
    for i, row in enumerate(rows):
        label, conf = model_service.predict(row)
        results.append(
            {
                "row": i,
                "predicted_class": label,
                "confidence": conf,
                "status": "success",
            }
        )
    return {"total": len(results), "predictions": results}


@router.get("/model/info")
def model_info():
    """Return basic model information."""
    return {
        "model_name": MODEL_NAME,
        "dataset": DATASET,
        "number_of_features": len(FEATURES),
        "supported_attack_classes": CLASSES,
        "model_mode": model_service.mode,
        "model_path": MODEL_PATH,
    }
