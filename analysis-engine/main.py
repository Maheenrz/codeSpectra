# analysis-engine/main.py

"""
CodeSpectra Analysis Engine API
===============================

A code clone detection API for educational institutions.

Endpoints:
- POST /api/analyze          : Analyze files (summary view)
- POST /api/analyze/detailed : Analyze files (detailed view with all scores)
- POST /api/pair/details     : Get detailed analysis for a specific pair

The system detects:
- Structural similarity (copy-paste, variable renaming)
- Semantic similarity (different code, same behavior)

Version: 2.0.0
"""

import time
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from engine.analyzer import CloneAnalyzer, AnalyzerConfig


# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="CodeSpectra Analysis Engine",
    description="Code clone detection for educational institutions",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# CONFIGURATION
# =============================================================================

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize analyzer
analyzer = CloneAnalyzer(AnalyzerConfig())


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def save_files(files: List[UploadFile], job_id: str) -> List[str]:
    """Save uploaded files and return paths"""
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    saved_paths = []
    for f in files:
        p = job_dir / f.filename
        content = await f.read()
        p.write_bytes(content)
        saved_paths.append(str(p))
    
    return saved_paths


def cleanup(job_dir: Path):
    """Clean up temporary files"""
    try:
        shutil.rmtree(job_dir)
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    """API information"""
    return {
        "service": "CodeSpectra Analysis Engine",
        "version": "2.0.0",
        "description": "Code clone detection for educational institutions",
        "endpoints": {
            "analyze": {
                "method": "POST",
                "path": "/api/analyze",
                "description": "Analyze files (summary view for list display)"
            },
            "analyze_detailed": {
                "method": "POST", 
                "path": "/api/analyze/detailed",
                "description": "Analyze files (detailed view with winnowing, AST, data-flow scores)"
            },
            "pair_details": {
                "method": "POST",
                "path": "/api/pair/details",
                "description": "Get detailed analysis for a specific file pair"
            }
        },
        "supported_languages": ["C++", "C", "Java", "Python"],
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_summary(files: List[UploadFile] = File(...)):
    """
    Analyze files for code similarity (SUMMARY VIEW).
    
    Use this for displaying list of pairs on frontend.
    Shows high-level scores without detailed breakdown.
    
    For detailed view (winnowing, AST, data-flow, etc.),
    use /api/analyze/detailed or /api/pair/details
    """
    
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")
    
    print(f"\n{'='*60}")
    print(f"📊 CodeSpectra Analysis (Summary): {len(files)} files")
    print(f"{'='*60}")
    
    job_id = f"analysis_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    
    try:
        # Save files
        saved_paths = await save_files(files, job_id)
        for f in files:
            print(f"  📄 {f.filename}")
        
        # Analyze (summary mode)
        report = analyzer.analyze(saved_paths, detailed=False)
        
        print(f"\n📋 Results:")
        print(f"   {report['class_analysis']['message']}")
        print(f"   Pairs needing review: {len(report['pairs_needing_review'])}")
        print(f"{'='*60}\n")
        
        return {"status": "success", **report}
        
    finally:
        cleanup(job_dir)


@app.post("/api/analyze/detailed")
async def analyze_detailed(files: List[UploadFile] = File(...)):
    """
    Analyze files for code similarity (DETAILED VIEW).
    
    Includes all detailed scores:
    
    Structural Details:
    - winnowing_score: Fingerprint-based similarity
    - ast_score: Abstract Syntax Tree similarity
    - metrics_score: Complexity metrics similarity
    - ml_score: ML model prediction
    - hybrid_score: Combined hybrid score
    
    Semantic Details:
    - control_flow_score: Loop/condition patterns
    - data_flow_score: Variable usage patterns
    - call_pattern_score: Function call patterns
    - structural_score: Code structure
    - behavioral_score: Overall behavior
    - behavioral_hash: Behavioral signature
    
    Use this when user wants full breakdown of all pairs.
    """
    
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")
    
    print(f"\n{'='*60}")
    print(f"📊 CodeSpectra Analysis (Detailed): {len(files)} files")
    print(f"{'='*60}")
    
    job_id = f"analysis_detailed_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    
    try:
        # Save files
        saved_paths = await save_files(files, job_id)
        for f in files:
            print(f"  📄 {f.filename}")
        
        # Analyze (detailed mode)
        report = analyzer.analyze(saved_paths, detailed=True)
        
        print(f"\n📋 Results:")
        print(f"   {report['class_analysis']['message']}")
        print(f"   Pairs needing review: {len(report['pairs_needing_review'])}")
        print(f"{'='*60}\n")
        
        return {"status": "success", **report}
        
    finally:
        cleanup(job_dir)


@app.post("/api/pair/details")
async def get_pair_details(files: List[UploadFile] = File(...)):
    """
    Get detailed analysis for a specific file pair.
    
    Use this when user clicks "View Details" button on a pair
    in the frontend list view.
    
    Upload exactly 2 files to compare.
    
    Returns full detailed breakdown including:
    - All structural scores (winnowing, AST, metrics, ML)
    - All semantic scores (control-flow, data-flow, call-pattern, behavioral)
    - Behavioral hashes for both files
    """
    
    if len(files) != 2:
        raise HTTPException(
            status_code=400, 
            detail="Exactly 2 files required for pair analysis"
        )
    
    print(f"\n{'='*60}")
    print(f"🔍 Pair Details: {files[0].filename} vs {files[1].filename}")
    print(f"{'='*60}")
    
    job_id = f"pair_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    
    try:
        # Save files
        saved_paths = await save_files(files, job_id)
        
        # Get detailed analysis for this pair
        result = analyzer.get_pair_details(saved_paths[0], saved_paths[1])
        
        print(f"   Structural: {result['structural']['score']:.0%}")
        print(f"   Semantic: {result['semantic']['score']:.0%}")
        print(f"{'='*60}\n")
        
        return {"status": "success", "pair": result}
        
    finally:
        cleanup(job_dir)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 CodeSpectra Analysis Engine v2.0")
    print("="*60)
    print("📍 Endpoints:")
    print("   POST /api/analyze          - Summary view (for list)")
    print("   POST /api/analyze/detailed - Detailed view (all scores)")
    print("   POST /api/pair/details     - Single pair details")
    print("="*60 + "\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)