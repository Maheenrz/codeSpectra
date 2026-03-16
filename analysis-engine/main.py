# analysis-engine/main.py
"""
CodeSpectra Analysis Engine API v2.1
=====================================

Endpoints:
  GET  /                              API info
  GET  /health                        Health check
  POST /api/analyze                   Multi-file summary analysis
  POST /api/analyze/detailed          Multi-file detailed analysis
  POST /api/pair/details              Single pair detail
  POST /api/analyze/assignment        Cross-student assignment analysis (async job)
  GET  /api/analyze/results/{job_id}  Poll job results
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

from engine.analyzer import CloneAnalyzer, AnalyzerConfig
from utils.zip_extractor import ZipExtractor

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CodeSpectra Analysis Engine",
    description="Code clone detection for educational institutions",
    version="2.1.0",
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

analyzer   = CloneAnalyzer(AnalyzerConfig())
executor   = ThreadPoolExecutor(max_workers=4)

# ─────────────────────────────────────────────────────────────────────────────
# In-memory job store
# {job_id: {status, assignment_id, analyzed_count, total_pairs,
#           remaining_count, clone_pairs, class_analysis, error, created_at}}
# ─────────────────────────────────────────────────────────────────────────────
jobs: Dict[str, Dict[str, Any]] = {}

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
    language:          str          = "cpp"
    extension_weights: Optional[Dict[str, float]] = None
    submissions:       List[StudentSubmission]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def save_files(files: List[UploadFile], job_id: str) -> List[str]:
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    paths = []
    for f in files:
        p = job_dir / f.filename
        p.write_bytes(await f.read())
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
    Calls analyze_for_assignment in retry rounds:
      - Round 1: process all pairs (30 s timeout each)
      - Round 2: retry timed-out pairs from round 1
      - Round 3: last attempt for any still failing
    After max rounds the job is marked 'completed' regardless — partial
    results are always available to the caller.
    """
    MAX_ROUNDS     = 3
    PAIR_TIMEOUT_S = 30

    submissions = [s.dict() for s in request.submissions]
    n           = len(submissions)
    total_pairs = n * (n - 1) // 2

    jobs[job_id]["total_pairs"] = total_pairs

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
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"]  = str(e)
            return

        # Accumulate results
        all_clone_pairs.extend(result.get("clone_pairs", []))

        # Pairs that timed out this round
        timed_out = {tuple(p) for p in result.get("remaining_pairs", [])}

        # Everything we attempted minus what timed out = newly done
        attempted  = all_pair_indices - skip_pairs
        newly_done = attempted - timed_out
        skip_pairs.update(newly_done)

        # Update job state (visible to polling)
        jobs[job_id].update({
            "analyzed_count":  len(skip_pairs),
            "remaining_count": len(timed_out),
            "clone_pairs":     all_clone_pairs,
            "class_analysis":  result.get("class_analysis", {}),
            "status":          "partial" if timed_out else "completed",
            "progress":        round(len(skip_pairs) / max(total_pairs, 1) * 100, 1),
        })

        if not timed_out:
            break   # All pairs processed — exit early

    # Mark complete regardless of any remaining (max rounds reached)
    jobs[job_id]["status"] = "completed"
    print(f"[Job {job_id}] ✅ Completed — "
          f"{jobs[job_id]['analyzed_count']}/{total_pairs} pairs analyzed, "
          f"{len(all_clone_pairs)} clone pairs found")


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "CodeSpectra Analysis Engine",
        "version": "2.1.0",
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
    return {"status": "healthy", "active_jobs": len(jobs)}


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
    """
    Kick off cross-student analysis for one assignment.
    Files are already on disk — paths are sent as JSON.

    Returns a job_id immediately. Poll /api/analyze/results/{job_id} for progress.
    """
    if len(request.submissions) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 student submissions required",
        )

    # Validate that all file paths exist
    missing = []
    for sub in request.submissions:
        for fp in sub.files:
            if not Path(fp).exists():
                missing.append(fp)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"File(s) not found on disk: {missing[:5]}",
        )

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
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

    # Run in thread pool (CPU-bound work; doesn't block the event loop)
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
    """
    Poll the status of an async assignment analysis job.

    status values:
      processing  — job is running, partial data may be available
      partial     — a round finished but some pairs still need retry
      completed   — all rounds done (full or best-effort results)
      failed      — unrecoverable error
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = jobs[job_id]
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
        "results":         job["clone_pairs"],  # alias for scheduler compatibility
    }


@app.post("/api/analyze/zip")
async def analyze_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Accept a .zip upload.

    Class zip (contains student sub-zips or folders):
      → runs cross-student analysis, same as /api/analyze/assignment
      → returns job_id to poll

    Project zip (single project):
      → runs intra-project NiCad batch detection synchronously
      → returns clone_classes immediately
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files accepted")

    job_id  = str(uuid.uuid4())
    zip_dir = UPLOAD_DIR / job_id
    zip_dir.mkdir(exist_ok=True)
    zip_path = zip_dir / file.filename
    zip_path.write_bytes(await file.read())

    extractor = ZipExtractor()
    try:
        mode, data = extractor.extract(str(zip_path))
    except Exception as e:
        cleanup(zip_dir)
        raise HTTPException(status_code=400, detail=f"ZIP extraction failed: {e}")

    # ── Single project mode: synchronous intra-project detection ─────────
    if mode == "project":
        all_files = data.get("project", [])
        if len(all_files) < 2:
            cleanup(zip_dir)
            return {"mode": "project", "error": "Less than 2 code files found in zip"}

        nicad = analyzer._structural.nicad
        nicad.clear_cache()
        result = nicad.detect_batch(all_files)
        cleanup(zip_dir)
        return {
            "mode":          "project",
            "status":        "completed",
            "total_files":   len(all_files),
            "clone_classes": result["clone_classes"],
            "total_fragments": result["total_fragments"],
            "total_clone_pairs": result["total_clone_pairs"],
            "processing_ms": result["processing_ms"],
        }

    # ── Class mode: async cross-student analysis ──────────────────────────
    students = list(data.items())  # [(name, [files]), ...]
    if len(students) < 2:
        cleanup(zip_dir)
        raise HTTPException(status_code=400, detail="Less than 2 students found in zip")

    # Build synthetic submission list
    submissions = [
        StudentSubmission(
            student_id    = idx + 1,
            submission_id = idx + 1,
            question_id   = None,
            files         = files,
        )
        for idx, (name, files) in enumerate(students)
    ]
    student_names = {idx + 1: name for idx, (name, _) in enumerate(students)}

    request = AssignmentAnalysisRequest(
        assignment_id     = 0,   # synthetic
        language          = "cpp",
        extension_weights = None,
        submissions       = submissions,
    )

    jobs[job_id] = {
        "status":          "processing",
        "assignment_id":   0,
        "mode":            "class_zip",
        "student_names":   student_names,
        "analyzed_count":  0,
        "total_pairs":     0,
        "remaining_count": 0,
        "progress":        0.0,
        "clone_pairs":     [],
        "class_analysis":  {},
        "error":           None,
        "created_at":      time.time(),
    }

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_assignment_analysis, job_id, request)

    return {
        "job_id":          job_id,
        "mode":            "class_zip",
        "status":          "processing",
        "total_students":  len(students),
        "student_names":   student_names,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 CodeSpectra Analysis Engine v2.1")
    print("=" * 60)
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)