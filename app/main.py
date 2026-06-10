from fastapi import FastAPI
from .config import settings
from .logger import logger
import os
import joblib
from .middleware import CustomTimingMiddleware
from .routers import router
from slowapi.middleware import SlowAPIMiddleware
from .limiter import limiter
from .redis_client import redis_client

app = FastAPI()
app.add_middleware(CustomTimingMiddleware)
app.include_router(router)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.get('/')
def root():
    return {"Message": "XGB Fraud Model API"}

@app.on_event('startup')
def on_startup():
    logger.info("Application starting up.")

    logger.info(redis_client.ping())

    if not os.path.exists(settings.MODEL_PATH):
        raise RuntimeError(f"Model file not found: {settings.MODEL_PATH}")
    
    app.state.model = joblib.load(settings.MODEL_PATH)
    
    logger.info(f"Loading model from {settings.MODEL_PATH}")

    if not hasattr(app.state.model, "predict_proba"):
        raise RuntimeError("Model does not support predict_proba")
    
    app.state.feature_order = app.state.model.get_booster().feature_names

    if not app.state.feature_order:
        raise RuntimeError("Feature order could not be loaded")
    
    logger.info(f"Loaded model with {len(app.state.feature_order)} features")

