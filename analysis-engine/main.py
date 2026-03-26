# analysis-engine/main.py
"""
CodeSpectra Analysis Engine API v3.0
=====================================
Updates:
 - Integrated dedicated RedisManager from services
 - Preserved multi-round retry logic for Type-4 analysis
 - Preserved structural thresholding and CSV generation
"""

import asyncio
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io

from engine.analyzer import CloneAnalyzer, AnalyzerConfig
from engine.report_generator import ReportGenerator
from utils.zip_extractor import ZipExtractor
from services.redis_manager import RedisManager  # <-- Imported your new manager

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CodeSpectra Analysis Engine",
    description="Code clone detection for educational institutions",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# CONFIGURATION & STATE MANAGEMENT
# =============================================================================

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

analyzer   = CloneAnalyzer(AnalyzerConfig())
executor   = ThreadPoolExecutor(max_workers=4)

# ── REDIS JOB STORE INTEGRATION ───────────
try:
    redis_manager = RedisManager()
except Exception as e:
    print(f"⚠️  CRITICAL: Redis not available. Jobs will NOT be saved. Error: {e}")
    redis_manager = None

# ── In-memory fallback when Redis is unavailable ─────────────────────────────
_job_store: Dict[str, Any] = {}

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    # Try Redis first
    if redis_manager and redis_manager.client:
        result = redis_manager.get_job(job_id)
        if result is not None:
            return result
    # Fall back to in-memory store
    return _job_store.get(job_id)

def save_job(job_id: str, data: Dict[str, Any]) -> None:
    # Always save to in-memory store (instant, never fails)
    _job_store[job_id] = data
    # Also persist to Redis if available
    if redis_manager and redis_manager.client:
        try:
            redis_manager.save_job(job_id, data)
        except Exception as e:
            print(f"⚠️  Redis save failed for job {job_id} (in-memory still available): {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class StudentSubmission(BaseModel):
    student_id:    int
    submission_id: int
    question_id:   Optional[int] = None
    files:         List[str]      # absolute paths on disk


class AssignmentAnalysisRequest(BaseModel):
    assignment_id:     int
    language:          str = "cpp"
    extension_weights: Optional[Dict[str, float]] = None
    submissions:       List[StudentSubmission]
    # Which detectors to run (all enabled by default)
    enable_type1: bool = True
    enable_type2: bool = True
    enable_type3: bool = True
    enable_type4: bool = True    


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def save_files(files: List[UploadFile], job_id: str) -> List[str]:
    """Save uploaded files to disk. Reads in 1MB chunks to avoid blocking."""
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    paths = []
    for f in files:
        safe_name = Path(f.filename).name if f.filename else f"file_{len(paths)}"
        p = job_dir / safe_name
        with p.open("wb") as out:
            while True:
                chunk = await f.read(1024 * 1024)   # 1 MB chunks
                if not chunk:
                    break
                out.write(chunk)
        paths.append(str(p))
    return paths


def cleanup(job_dir: Path) -> None:
    try:
        shutil.rmtree(job_dir)
    except Exception as e:
        print(f"⚠️  Cleanup: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Background job logic
# ─────────────────────────────────────────────────────────────────────────────

def _run_assignment_analysis(job_id: str, request: AssignmentAnalysisRequest) -> None:
    """
    Runs in a thread-pool executor.
    Calls analyze_for_assignment in retry rounds.
    """
    MAX_ROUNDS     = 3
    PAIR_TIMEOUT_S = 60 
    job_state = get_job(job_id)
    if not job_state:
        # Should never happen with in-memory fallback, but handle gracefully
        print(f"⚠️  Job {job_id} not in store at task start — rebuilding from request")
        job_state = {
            "status": "processing", "assignment_id": request.assignment_id,
            "analyzed_count": 0, "total_pairs": 0, "remaining_count": 0,
            "progress": 0.0, "clone_pairs": [], "class_analysis": {},
            "error": None, "created_at": time.time(),
        }
        save_job(job_id, job_state)

    submissions = [s.dict() for s in request.submissions]
    n           = len(submissions)
    total_pairs = n * (n - 1) // 2

    job_state["total_pairs"] = total_pairs
    save_job(job_id, job_state)

    all_clone_pairs: List[Dict] = []
    skip_pairs = set()   # pairs already successfully processed
    all_pair_indices = {
        (i, j) for i in range(n) for j in range(i + 1, n)
    }

    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"[Job {job_id}] Round {round_num}/{MAX_ROUNDS} — "
              f"{len(all_pair_indices - skip_pairs)} pairs remaining")

        try:
            result = analyzer.analyze_for_assignment(
                student_submissions=submissions,
                language=request.language,
                extension_weights=request.extension_weights or {},
                pair_timeout_seconds=PAIR_TIMEOUT_S,
                skip_pairs=skip_pairs,
            )
        except Exception as e:
            print(f"[Job {job_id}] Round {round_num} error: {e}")
            job_state = get_job(job_id)
            job_state["status"] = "failed"
            job_state["error"]  = str(e)
            save_job(job_id, job_state)
            return

        # Fetch latest state to ensure we don't overwrite other data
        job_state = get_job(job_id)

        # Accumulate results — attach student names for class_zip mode
        new_pairs = result.get("clone_pairs", [])
        student_names = job_state.get("student_names", {})
        for cp in new_pairs:
            if student_names:
                cp["student_a_name"] = student_names.get(str(cp.get("student_a_id")), "")
                cp["student_b_name"] = student_names.get(str(cp.get("student_b_id")), "")
        all_clone_pairs.extend(new_pairs)

        timed_out = {tuple(p) for p in result.get("remaining_pairs", [])}
        attempted  = all_pair_indices - skip_pairs
        newly_done = attempted - timed_out
        skip_pairs.update(newly_done)

        # Update job state (visible to polling)
        job_state.update({
            "analyzed_count":  len(skip_pairs),
            "remaining_count": len(timed_out),
            "clone_pairs":     all_clone_pairs,
            "class_analysis":  result.get("class_analysis", {}),
            "status":          "partial" if timed_out else "completed",
            "progress":        round(len(skip_pairs) / max(total_pairs, 1) * 100, 1),
        })
        save_job(job_id, job_state)

        if not timed_out:
            break   # All pairs processed — exit early

    # Mark complete regardless of any remaining (max rounds reached)
    job_state = get_job(job_id)
    job_state["status"] = "completed"
    save_job(job_id, job_state)
    
    print(f"[Job {job_id}] ✅ Completed — "
          f"{job_state['analyzed_count']}/{total_pairs} pairs analyzed, "
          f"{len(all_clone_pairs)} clone pairs found")


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "CodeSpectra Analysis Engine",
        "version": "3.0.0",
        "endpoints": {
            "analyze":             "POST /api/analyze",
            "analyze_detailed":    "POST /api/analyze/detailed",
            "pair_details":        "POST /api/pair/details",
            "analyze_assignment":  "POST /api/analyze/assignment",
            "poll_results":        "GET  /api/analyze/results/{job_id}",
        },
    }

@app.get("/health")
def health():
    return {"status": "healthy", "redis_connected": redis_manager is not None}

@app.post("/api/analyze")
async def analyze_summary(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")
    job_id  = f"summary_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths  = await save_files(files, job_id)
        report = analyzer.analyze(paths, detailed=False)
        return {"status": "success", **report}
    finally:
        cleanup(job_dir)


@app.post("/api/analyze/detailed")
async def analyze_detailed(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")

    SYNC_FILE_LIMIT = 30
    if len(files) > SYNC_FILE_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Too many files ({len(files)}) for synchronous analysis. "
                f"Please use a ZIP upload via POST /api/analyze/zip instead. "
            ),
        )

    job_id  = f"detailed_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths  = await save_files(files, job_id)
        report = analyzer.analyze(paths, detailed=True)
        return {"status": "success", **report}
    finally:
        cleanup(job_dir)


@app.post("/api/pair/details")
async def get_pair_details(files: List[UploadFile] = File(...)):
    if len(files) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 files required")
    job_id  = f"pair_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths  = await save_files(files, job_id)
        result = analyzer.get_pair_details(paths[0], paths[1])
        return {"status": "success", "pair": result}
    finally:
        cleanup(job_dir)


@app.post("/api/analyze/assignment")
async def analyze_assignment(
    request: AssignmentAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    """Kick off cross-student analysis for one assignment."""
    if len(request.submissions) < 2:
        raise HTTPException(status_code=400, detail="At least 2 student submissions required")

    missing = []
    for sub in request.submissions:
        for fp in sub.files:
            if not Path(fp).exists():
                missing.append(fp)
    if missing:
        raise HTTPException(status_code=400, detail=f"File(s) not found on disk: {missing[:5]}")

    job_id = str(uuid.uuid4())
    job_state = {
        "status":          "processing",
        "assignment_id":   request.assignment_id,
        "analyzed_count":  0,
        "total_pairs":     0,
        "remaining_count": 0,
        "progress":        0.0,
        "clone_pairs":     [],
        "class_analysis":  {},
        "error":           None,
        "created_at":      time.time(),
    }
    save_job(job_id, job_state)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_assignment_analysis, job_id, request)

    return {
        "job_id":        job_id,
        "status":        "processing",
        "assignment_id": request.assignment_id,
        "total_students": len(request.submissions),
    }


@app.get("/api/analyze/results/{job_id}")
def get_job_results(job_id: str):
    """Poll the status of an async assignment analysis job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return {
        "job_id":          job_id,
        "status":          job["status"],
        "assignment_id":   job["assignment_id"],
        "progress":        job.get("progress", 0.0),
        "analyzed_count":  job["analyzed_count"],
        "total_pairs":     job["total_pairs"],
        "remaining_count": job.get("remaining_count", 0),
        "clone_pairs":     job["clone_pairs"],
        "class_analysis":  job["class_analysis"],
        "error":           job.get("error"),
        "results":         job["clone_pairs"], 
    }


@app.post("/api/analyze/zip")
async def analyze_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Accept a .zip upload containing student sub-zips or student folders."""
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files accepted")

    job_id  = str(uuid.uuid4())
    zip_dir = UPLOAD_DIR / job_id
    zip_dir.mkdir(exist_ok=True)
    zip_path = zip_dir / (file.filename or "upload.zip")

    try:
        with zip_path.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    except Exception as e:
        cleanup(zip_dir)
        raise HTTPException(status_code=500, detail=f"Failed to save ZIP: {e}")

    # The updated ZipExtractor with recursive logic handles nested files here
    extractor = ZipExtractor()
    try:
        mode, data = extractor.extract(str(zip_path))
    except Exception as e:
        cleanup(zip_dir)
        raise HTTPException(status_code=400, detail=f"ZIP extraction failed: {e}")

    if mode == "project":
        all_files = data.get("project", [])
        if len(all_files) < 2:
            cleanup(zip_dir)
            return {"mode": "project", "status": "completed", "job_id": job_id, "error": "Less than 2 files found"}
        
        try:
            report = analyzer.analyze(all_files, detailed=False)
            return {"mode": "project", "status": "completed", "job_id": job_id, **report}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
        finally:
            cleanup(zip_dir)

    # Class ZIP Mode
    students = list(data.items())
    if len(students) < 2:
        cleanup(zip_dir)
        raise HTTPException(status_code=400, detail=f"Less than 2 students found in ZIP")

    submissions = [
        StudentSubmission(
            student_id    = idx + 1,
            submission_id = idx + 1,
            question_id   = None,
            files         = files_list,
        )
        for idx, (name, files_list) in enumerate(students)
    ]
    student_names = {str(idx + 1): name for idx, (name, _) in enumerate(students)}

    request = AssignmentAnalysisRequest(
        assignment_id     = 0,
        language          = "cpp",
        extension_weights = None,
        submissions       = submissions,
    )

    job_state = {
        "status":          "processing",
        "assignment_id":   0,
        "mode":            "class_zip",
        "student_names":   student_names,
        "analyzed_count":  0,
        "total_pairs":     len(students) * (len(students) - 1) // 2,
        "remaining_count": 0,
        "progress":        0.0,
        "clone_pairs":     [],
        "class_analysis":  {},
        "error":           None,
        "created_at":      time.time(),
    }
    save_job(job_id, job_state)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_assignment_analysis, job_id, request)

    return {
        "job_id":         job_id,
        "mode":           "class_zip",
        "status":         "processing",
        "total_students": len(students),
        "student_names":  student_names,
    }

# ─────────────────────────────────────────────────────────────────────────────
# CSV Report endpoints
# ─────────────────────────────────────────────────────────────────────────────

_report_gen = ReportGenerator()

@app.post("/api/report/csv")
async def generate_csv_report(
    files: List[UploadFile] = File(...),
    assignment_id: str = "",
    language: str = "cpp",
    mode: str = "summary",
    detailed: bool = True,
):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")

    job_id  = f"report_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths  = await save_files(files, job_id)
        report = analyzer.analyze(paths, detailed=True)

        csv_str = _report_gen.from_analysis_response(
            report, assignment_id=assignment_id, language=language, mode=mode, detailed=detailed,
        )

        filename = f"codespectra_{mode}_{assignment_id or 'analysis'}_{int(time.time())}.csv"
        return StreamingResponse(
            io.StringIO(csv_str),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        cleanup(job_dir)


@app.get("/api/report/csv/{job_id}")
def generate_csv_from_job(job_id: str, assignment_id: str = "", language: str = "cpp"):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job["status"] not in ("completed", "partial"):
        raise HTTPException(status_code=400, detail=f"Job not yet complete (status={job['status']}). Poll first.")

    clone_pairs = job.get("clone_pairs", [])
    csv_str     = _report_gen.from_clone_pairs(
        clone_pairs, assignment_id=assignment_id or str(job.get("assignment_id", "")), language=language,
    )

    filename = f"codespectra_assignment_{assignment_id or job_id}_{int(time.time())}.csv"
    return StreamingResponse(
        io.StringIO(csv_str),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 CodeSpectra Analysis Engine v3.0 (Redis Backed)")
    print("=" * 60)
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)