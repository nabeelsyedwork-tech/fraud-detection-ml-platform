from fastapi import HTTPException, Request, APIRouter, UploadFile, File, Depends
import uuid
import io
import pandas as pd
from .schemas import (HealthResponse, PredictionResponse, Transaction, metrics)
from .config import settings
from .logger import logger
from .services import (preprocess, predict, postprocess)
import time
from .limiter import limiter
from .redis_client import redis_client
from typing import cast
from app.auth import verify_user

router = APIRouter()
MAX_SIZE_BYTES = 5 * 1024 * 1024
MAX_SIZE_MB = 5

@router.get("/health")
def health():
    return {
        "status": "healthy"
    }

@router.get("/health/details", response_model=HealthResponse)
def health_details(request: Request):
    return HealthResponse(
        status="healthy",
        model_loaded=hasattr(
            request.app.state,
            "model"
        ),
        feature_count=len(request.app.state.feature_order)
    )
    
@router.get("/model/info")
def model_info(request:Request, user: str = Depends(verify_user)):
    return {
    "model_name": "xgb_fraud_detector",
    "model_version": settings.MODEL_VERSION,
    "n_features": len(
        request.app.state.feature_order
    ),
    "threshold": settings.THRESHOLD
}

@router.post("/predict",response_model=PredictionResponse)
@limiter.limit("60/minute")
def predict_api(transaction: Transaction, request: Request, user: str = Depends(verify_user)):
    request_id = str(uuid.uuid4())
    try:
        feature_order = request.app.state.feature_order
        model = request.app.state.model
        features = preprocess(transaction,feature_order)
        prob, label,inference_time_ms  = predict(features=features,model=model)
        logger.info(
            {
                "user": user,
                "request_id": request_id,
                "amount": transaction.Amount,
                "prediction": round(prob, 4),
                "is_fraud": bool(label),
                "inference_time_ms": round(inference_time_ms, 2)
            }
        )
        result = postprocess(prob, label,request_id)
        logger.info(f"Prediction made: prob={prob}")
        redis_client.incr("total_predictions")

        redis_client.incr(
            "total_fraud_predictions",
            int(label)
        )

        redis_client.incrbyfloat(
            "total_inference_time_ms",
            inference_time_ms
        )

        return result
    
    except HTTPException:
        raise

    except Exception:
        logger.exception(
            f"Prediction failed request_id={request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/predict/csv")
@limiter.limit("10/minute")
async def predict_csv(request:Request, file:UploadFile = File(...), user: str = Depends(verify_user)):
    if not file.filename:
        raise HTTPException(
            status_code=400, 
            detail="Uploaded file is missing a valid filename."
        )
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Please upload a .csv file."
        )


    request_id = str(uuid.uuid4())

    try:
        request_start = time.perf_counter()
        parse_start = time.perf_counter()
        
        contents = await file.read()
        if len(contents) > MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds {MAX_SIZE_MB} MB"
            )
        df = pd.read_csv(io.BytesIO(contents))

        parse_time_ms = (
            time.perf_counter() - parse_start
        ) * 1000
        feature_order = request.app.state.feature_order
        missing_features = [feat for feat in feature_order if feat not in df.columns]

        if missing_features:
            raise HTTPException(status_code=400, detail=f"Uploaded CSV is missing required columns: {missing_features}")
        
        X = df[feature_order].values

        model = request.app.state.model

        inference_start = time.perf_counter()

        probabilities = model.predict_proba(X)[:,1]

        model_inference_ms = (
            time.perf_counter() - inference_start
        ) * 1000

        df["fraud_probability"] = probabilities
        df["is_fraud"] = probabilities > settings.THRESHOLD

        total_transactions = len(df)
        fraud_count = int((probabilities > settings.THRESHOLD).sum())
        total_amount = float(df["Amount"].sum())
        
        total_request_ms = (time.perf_counter() - request_start) * 1000
        redis_client.incr(
            "total_csv_uploads"
        )
        redis_client.incr(
            "total_predictions",
            total_transactions
        )

        redis_client.incr(
            "total_fraud_predictions",
            fraud_count
        )

        redis_client.incrbyfloat(
            "total_inference_time_ms",
            model_inference_ms
        )


        logger.info({
        "event": "csv_bulk_inference",
        "user": user,
        "request_id": request_id,
        "rows": total_transactions,
        "fraud_count": fraud_count,
        "total_amount": round(total_amount, 2),
        "parse_time_ms": round(parse_time_ms, 2),
        "model_inference_ms": round(model_inference_ms, 2),
        "total_request_ms": round(total_request_ms, 2)
    })

        return {"results": df[["Time", "Amount", "fraud_probability", "is_fraud"]].to_dict(orient="records")}

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"CSV prediction failed request_id={request_id}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/metrics")
async def get_metrics(user: str = Depends(verify_user)):
    raw_predictions =  cast(str | None,redis_client.get("total_predictions"))
    total_predictions = int(raw_predictions or 0)

    raw_csv_uploads =  cast(str | None,redis_client.get("total_csv_uploads"))
    total_csv_uploads = int(raw_csv_uploads or 0)

    raw_fraud_predictions =  cast(str | None,redis_client.get("total_fraud_predictions"))
    total_fraud_predictions = int(raw_fraud_predictions or 0)

    raw_inference_time =  cast(str | None,redis_client.get("total_inference_time_ms"))
    total_inference_time_ms = float(raw_inference_time or 0)

    avg_inference_per_prediction_ms = 0

    if total_predictions:
        avg_inference_per_prediction_ms = (
            total_inference_time_ms
            / total_predictions
        )
    fraud_rate = 0

    if total_predictions:
        fraud_rate = (
            total_fraud_predictions
            / total_predictions
        ) * 100

    return {
        "total_predictions": total_predictions,
        "total_csv_uploads": total_csv_uploads,
        "total_fraud_predictions": total_fraud_predictions,
        "avg_inference_per_prediction_ms": round(avg_inference_per_prediction_ms, 4),
        "fraud_rate_percent": round(fraud_rate, 2)
    }