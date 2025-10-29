from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict

class PredictRequest(BaseModel):
    text: Optional[str] = None
    metadata: Optional[Dict] = None

class PredictResponse(BaseModel):
    prediction: str
    confidence: float

app = FastAPI(title="ClinIQ-AI Backend")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """Dummy inference endpoint. Always returns a fixed response.
    Expects JSON like {"text": "some input"} but accepts any JSON payload.
    """
    # Dummy response — replace with real model loading/inference later
    return {"prediction": "negative", "confidence": 0.95}
