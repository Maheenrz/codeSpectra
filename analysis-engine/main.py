from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="CodeSpectra Analysis Engine")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "CodeSpectra Analysis Engine is running!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analyze/test")
def test_analyze():
    return {
        "message": "Analysis API is working!",
        "detectors": ["Type1", "Type2", "Type3", "Type4", "CRD"]
    }
