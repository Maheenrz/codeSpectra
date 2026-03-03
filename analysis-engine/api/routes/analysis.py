from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import time
import traceback

# Import Detectors
from detectors.type1.hash_method import HashMethod
from detectors.type1.ast_exact_method import ASTExactMethod
from detectors.type1.string_method import StringMethod

router = APIRouter()

@router.post("/analyze")
async def analyze_project(
    files: list[UploadFile] = File(...), 
    types: str = Form(...),
    mode: str = Form(...)
):
    print("🔹 [DEBUG] Request Received!")
    
    try:
        # --- 1. PREPARE FILES ---
        project_files = []
        for file in files:
            content = await file.read()
            try:
                # Try decoding as text (ignore binary files)
                text_content = content.decode('utf-8', errors='ignore')
                project_files.append({"path": file.filename, "content": text_content})
            except:
                continue

        results_data = {}

        # --- 2. RUN TYPE 1 DETECTORS ---
        if "type1" in types:
            print("🔹 [DEBUG] Running Type 1 Analysis...")
            # ...existing code...
            results_data["type1"] = {
                "total_unique_clones": max_clones,
                "best_method": best_method,
                "method_results": type1_results
            }
        # ...existing code for type3, type4, etc...
        print("\n🔸 [BACKEND] JSON Response:")
        import json
        print(json.dumps(results_data, indent=2, ensure_ascii=False))
        return results_data

    except Exception as e:
        print("❌ [ERROR] CRITICAL FAILURE:")
        traceback.print_exc()
        # ...existing code...