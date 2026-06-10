import time
import numpy as np
from .schemas import (Transaction, PredictionResponse)
from .config import settings

def preprocess(data: Transaction,Feature_Order):
    data_dict = data.model_dump()
    return np.array([data_dict[f] for f in Feature_Order]).reshape(1, -1)

def predict(features: np.ndarray,model):
    start = time.perf_counter()
    prob = model.predict_proba(features)[0][1]  
    inference_time_ms = (time.perf_counter() - start) * 1000
    label = int(prob > settings.THRESHOLD)
    return prob, label, inference_time_ms

def postprocess(prob, label,requestid):
    return PredictionResponse(
    request_id=requestid,
    fraud_probability=float(round(prob,4)),
    is_fraud=bool(label)
)