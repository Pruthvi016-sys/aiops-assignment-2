import os
from contextlib import asynccontextmanager

import joblib
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_PATH = "model.joblib"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL_SECONDS = 300

state = {"model": None, "redis": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    state["redis"] = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
    )
    print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    yield
    state.clear()

app = FastAPI(title="Spam Detection API", lifespan=lifespan)

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str
    cached: bool

def cache_key(text: str) -> str:
    return f"predict:{text}"

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    r = state["redis"]
    key = cache_key(req.text)

    cached_label = r.get(key)
    if cached_label is not None:
        return {"label": cached_label, "cached": True}

    model = state["model"]
    label = model.predict([req.text])[0]
    r.setex(key, CACHE_TTL_SECONDS, label)

    return {"label": label, "cached": False}

@app.get("/healthz")
def healthz():
    if state["model"] is not None:
        return {"status": "ok"}
    return JSONResponse(status_code=503, content={"status": "loading"})