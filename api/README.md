# IDS API (basic)

## Run

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open: http://localhost:8000/docs

## Endpoints

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/` | Status |
| GET | `/health` | Health |
| POST | `/predict` | One prediction (JSON) |
| POST | `/batch_predict` | CSV predictions |
| GET | `/model/info` | Model info |

## Example `POST /predict`

```json
{
  "features": {
    "Flow Duration": 300000.0,
    "Fwd IAT Std": 1250.5,
    "Average Packet Size": 210.5
  }
}
```

Response:

```json
{
  "predicted_class": "DDoS",
  "confidence": 0.87,
  "status": "success"
}
```

> Uses a **placeholder** until `models/stacking_ensemble.joblib` exists.
