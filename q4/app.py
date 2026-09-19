from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_PATH = "model.joblib"
VERSION = "v2"
state = {"model": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    yield
    state.clear()

app = FastAPI(title="Spam Detection API", lifespan=lifespan)

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    model = state["model"]
    label = model.predict([req.text])[0]
    return {"label": label}

@app.get("/healthz")
def healthz():
    if state["model"] is not None:
        return {"status": "ok", "version": VERSION}
    return JSONResponse(status_code=503, content={"status": "loading", "version": VERSION})