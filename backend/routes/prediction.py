from fastapi import APIRouter, HTTPException
from models.schemas import ProcessInput, PredictionResponse
from services.ml_service import ml_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["prediction"])

@router.post("/predict")
async def predict(input_data: ProcessInput):
    try:
        result = ml_service.predict(input_data.model_dump())
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeseries")
async def get_timeseries():
    try:
        return ml_service.get_time_series()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batches")
async def get_batches():
    try:
        return ml_service.get_batch_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "ok", "models_loaded": len(ml_service.quality_models)}
