import json
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, Form
from detectors.type1.hash_method import HashMethod

router = APIRouter()

@router.post("/analyze")
async def analyze_project(
    files: List[UploadFile] = File(...),
    types: str = Form(...),  # Received as JSON string from frontend
    mode: str = Form(...)
):
    # 1. Read uploaded files into memory
    project_files = []
    for file in files:
        content = await file.read()
        try:
            # Try decoding as text (skip binary files like zip/images for now)
            text_content = content.decode('utf-8')
            project_files.append({
                "path": file.filename,
                "content": text_content
            })
        except UnicodeDecodeError:
            print(f"Skipping binary file: {file.filename}")

    results_data = {}

    # 2. Run Type 1 Detection (Hash Method)
    # Note: We simulate the 'comparison' format the frontend needs
    start_time = time.time()
    
    detector = HashMethod()
    clones = detector.detect(project_files, project_id="test_session")
    
    execution_time = round((time.time() - start_time) * 1000, 2)

    # 3. Format Response for Frontend
    # The frontend expects a specific structure to generate the table
    results_data["type1"] = {
        "total_unique_clones": len(clones),
        "best_method": "Hash-Based Exact Match",
        "consensus_clones": len(clones),
        "method_results": [
            {
                "method_name": "Hash-Based Exact Match",
                "clones_found": len(clones),
                "execution_time_ms": execution_time,
                "accuracy_score": 100  # Placeholder for Type 1
            },
            # We can add a dummy entry to show comparison UI working
            {
                "method_name": "AST Method (Coming Soon)",
                "clones_found": 0,
                "execution_time_ms": 0,
                "accuracy_score": 0
            }
        ]
    }

    return results_data