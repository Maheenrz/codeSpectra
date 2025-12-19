from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi import FastAPI, HTTPException
import os
import json
from app.detectors.type2_detector import detect_type2_clones
app = FastAPI(title="CodeSpectra Analysis Engine")

# Base directory where files are stored (shared Docker volume)
# This path must match the volume mapping in your docker-compose.yml: ./uploads:/app/uploads
UPLOAD_DIR = "/app/uploads"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the analysis route
app.include_router(analysis.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "CodeSpectra Engine Running"}

# --- API Endpoint for Type 2 Analysis ---
@app.post("/analyze/type2/")
def analyze_type2(assignment_name: str):
    """
    Analyzes all files in a specific assignment folder for Type 2 clones.
    """
    # 1. Construct the full path to the assignment directory
    assignment_dir = os.path.join(UPLOAD_DIR, assignment_name)
    
    if not os.path.isdir(assignment_dir):
        raise HTTPException(
            status_code=404,
            detail=f"Assignment directory not found at {assignment_dir}"
        )

    # Define the file patterns to search for (e.g., C/C++ files)
    # You can adjust this list based on your actual assignment files
    language_patterns = ['*.c', '*.cpp', '*.h']

    # 2. Run the detection logic
    clone_results = detect_type2_clones(assignment_dir, language_patterns)
    
    # 3. Format and return the results
    response_data = []
    for code_hash, paths in clone_results.items():
        response_data.append({
            "clone_hash": code_hash,
            "clone_count": len(paths),
            "files": [os.path.basename(p) for p in paths]
        })

    return {
        "assignment": assignment_name,
        "clone_type": "Type 2 (Renamed Identifiers)",
        "results": response_data
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "CodeSpectra Analysis Engine is running!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def read_root():
    return {"status": "Analysis Engine is Online", "detector_ready": "Type 2"}


@app.get("/api/analyze/test")
def test_analyze():
    return {
        "message": "Analysis API is working!",
        "detectors": ["Type1", "Type2", "Type3", "Type4", "CRD"]
    }
