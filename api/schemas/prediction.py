"""Request / response schemas."""

from typing import Dict, List
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Network traffic features (all 30 mRMR features as floats)."""

    features: Dict[str, float] = Field(
        ...,
        example={
            "Flow Duration": 300000.0,
            "Fwd IAT Std": 1250.5,
            "Average Packet Size": 210.5,
        },
    )


class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    status: str
