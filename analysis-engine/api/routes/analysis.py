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
            
            # We run all 3 methods to compare them
            detectors = [
                HashMethod(),
                ASTExactMethod(),
                StringMethod()
            ]
            
            type1_results = []
            
            for detector in detectors:
                start_time = time.time()
                clones = detector.detect(project_files, "session")
                duration = round((time.time() - start_time) * 1000, 2)
                
                print(f"   👉 Method {detector.name} found {len(clones)} clones in {duration}ms")
                
                type1_results.append({
                    "method_name": detector.name,
                    "clones_found": len(clones),
                    "execution_time_ms": duration,
                    "accuracy_score": 100 if len(clones) > 0 else 0 
                })

            # --- BUG FIX IS HERE ---
            # Old logic: len(all) // len(detectors) -> Resulted in 0
            # New logic: Take the MAX clones found by any method.
            # If Hash found 1 and AST found 0, the total is 1.
            max_clones = 0
            best_method = "None"
            fastest_time = float('inf')

            for res in type1_results:
                if res['clones_found'] > max_clones:
                    max_clones = res['clones_found']
                    best_method = res['method_name']
                    fastest_time = res['execution_time_ms']
                elif res['clones_found'] == max_clones and res['clones_found'] > 0:
                    # Tie-breaker: Pick the faster one
                    if res['execution_time_ms'] < fastest_time:
                        best_method = res['method_name']
                        fastest_time = res['execution_time_ms']
            
            results_data["type1"] = {
                "total_unique_clones": max_clones,
                "best_method": best_method,
                "method_results": type1_results
            }

        return results_data

    except Exception as e:
        print("❌ [ERROR] CRITICAL FAILURE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))