"""Load model with joblib, or use a simple placeholder."""

from pathlib import Path
import random

from config import MODEL_PATH, CLASSES, FEATURES


class ModelService:
    def __init__(self):
        self.model = None
        self.mode = "placeholder"
        self._load()

    def _load(self):
        path = Path(MODEL_PATH)
        if path.exists():
            import joblib
            self.model = joblib.load(path)
            self.mode = "trained"
        else:
            self.model = None
            self.mode = "placeholder"

    def predict(self, features: dict) -> tuple[str, float]:
        # Real model later
        if self.model is not None:
            x = [[features.get(f, 0.0) for f in FEATURES]]
            label = str(self.model.predict(x)[0])
            conf = 0.9
            if hasattr(self.model, "predict_proba"):
                conf = float(max(self.model.predict_proba(x)[0]))
            return label, conf

        # Placeholder for first review (no trained file yet)
        label = random.choice(CLASSES)
        conf = round(random.uniform(0.6, 0.99), 4)
        return label, conf


model_service = ModelService()
