"""
IDS FastAPI Backend — basic version (first review).

Run:
    cd api
    uvicorn main:app --reload --port 8000

Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from routers.predict import router

app = FastAPI(
    title="IDS API",
    description="SMOTE Stacking Ensemble Intrusion Detection — basic backend",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    """API status."""
    return {"status": "online", "message": "IDS API is running"}


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy"}
