"""
services/kronos-embedder/main.py
FastAPI microservice serving Kronos embeddings and generative reality cones.
"""

import time
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from extractor import KronosPatternEngine

app = FastAPI(
    title="XPredictor Kronos Embedding Service",
    description="High-throughput financial microstructure embedding and Monte Carlo forward path generator",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = KronosPatternEngine()


class EmbedRequest(BaseModel):
    # Shape: (N, L, 6) where 6 is [open, high, low, close, volume, amount]
    windows: List[List[List[float]]] = Field(..., description="Batch of K-line windows of shape (N, L, 6)")


class EmbedResponse(BaseModel):
    embeddings: List[List[float]] = Field(..., description="L2-normalized 768-D embedding vectors")
    latency_ms: float
    batch_size: int
    vector_dim: int


class PredictConeRequest(BaseModel):
    window: List[List[float]] = Field(..., description="Candle window of shape (L, 6)")
    pred_len: int = Field(20, ge=1, le=100)
    sample_count: int = Field(100, ge=10, le=1000)
    temperature: float = Field(1.0, ge=0.1, le=2.0)
    top_p: float = Field(0.90, ge=0.1, le=1.0)


class PredictConeResponse(BaseModel):
    pred_len: int
    sample_count: int
    last_close: float
    quantiles: dict
    latency_ms: float


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "kronos-embedder",
        "vector_dim": engine.d_model,
        "max_context": engine.max_context,
        "device": str(getattr(engine, "device", "cpu"))
    }


@app.post("/embed", response_model=EmbedResponse)
def get_embeddings(request: EmbedRequest):
    t0 = time.perf_counter()
    if not request.windows:
        raise HTTPException(status_code=400, detail="Windows list cannot be empty")

    try:
        np_windows = [np.array(w, dtype=np.float32) for w in request.windows]
        embeddings = engine.encode_batch(np_windows)
        latency = (time.perf_counter() - t0) * 1000.0

        return EmbedResponse(
            embeddings=embeddings.tolist(),
            latency_ms=round(latency, 2),
            batch_size=len(np_windows),
            vector_dim=engine.d_model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


@app.post("/predict-cone", response_model=PredictConeResponse)
def get_predict_cone(request: PredictConeRequest):
    t0 = time.perf_counter()
    try:
        window_np = np.array(request.window, dtype=np.float32)
        result = engine.predict_cone(
            ohlcv_window=window_np,
            pred_len=request.pred_len,
            sample_count=request.sample_count,
            temperature=request.temperature,
            top_p=request.top_p
        )
        latency = (time.perf_counter() - t0) * 1000.0
        return PredictConeResponse(
            pred_len=result["pred_len"],
            sample_count=result["sample_count"],
            last_close=result["last_close"],
            quantiles=result["quantiles"],
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cone generation error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
