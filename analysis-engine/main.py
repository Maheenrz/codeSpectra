# analysis-engine/main.py
"""
CodeSpectra Analysis Engine API v3.0
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import asyncio
import shutil
import time
import uuid
import math
import logging
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from engine.analyzer import CloneAnalyzer, AnalyzerConfig
from engine.report_generator import ReportGenerator
from utils.zip_extractor import ZipExtractor
from services.redis_manager import RedisManager
from detectors.type3.fragment_comparator import compare_fragments

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

analyzer = CloneAnalyzer(AnalyzerConfig())
executor = ThreadPoolExecutor(max_workers=2)

try:
    redis_manager = RedisManager()
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_manager = None

_job_store: Dict[str, Any] = {}

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    if redis_manager and redis_manager.client:
        result = redis_manager.get_job(job_id)
        if result is not None:
            return result
    return _job_store.get(job_id)

def save_job(job_id: str, data: Dict[str, Any]) -> None:
    _job_store[job_id] = data
    if redis_manager and redis_manager.client:
        try:
            redis_manager.save_job(job_id, data)
        except Exception as e:
            logger.warning(f"Redis save failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class StudentSubmission(BaseModel):
    student_id: int
    submission_id: int
    question_id: Optional[int] = None
    files: List[str]

class AssignmentAnalysisRequest(BaseModel):
    assignment_id: int
    language: str = "cpp"
    extension_weights: Optional[Dict[str, float]] = None
    submissions: List[StudentSubmission]
    enable_type1: bool = True
    enable_type2: bool = True
    enable_type3: bool = True
    enable_type4: bool = True

class ChunkedAnalysisRequest(BaseModel):
    job_id: str
    chunk_size: int = Field(default=500, ge=50, le=2000)
    chunk_index: int = Field(default=0, ge=0)
    assignment_id: Optional[int] = None
    language: str = "cpp"
    enable_type1: bool = True
    enable_type2: bool = True
    enable_type3: bool = True
    enable_type4: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def save_upload(file: UploadFile, dest: Path) -> None:
    with dest.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

async def save_files(files: List[UploadFile], job_id: str) -> List[str]:
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    paths = []
    for f in files:
        safe_name = Path(f.filename).name if f.filename else f"file_{len(paths)}"
        p = job_dir / safe_name
        await save_upload(f, p)
        paths.append(str(p))
    return paths

def cleanup(job_dir: Path) -> None:
    try:
        shutil.rmtree(job_dir)
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")

def _make_job(job_id: str, total_pairs: int = 0, student_names: Dict = None) -> Dict:
    return {
        "job_id":          job_id,
        "status":          "processing",
        "total_pairs":     total_pairs,
        "analyzed_count":  0,
        "remaining_count": 0,
        "progress":        0.0,
        "clone_pairs":     [],
        "results":         [],
        "class_analysis":  {},
        "student_names":   student_names or {},
        "error":           None,
        "created_at":      time.time(),
        "updated_at":      time.time(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "CodeSpectra Analysis Engine",
        "version": "3.0.0",
        "endpoints": {
            "health":       "GET /health",
            "analyze_zip":  "POST /api/analyze/zip",
            "poll_results": "GET /api/analyze/results/{job_id}",
            "csv_report":   "POST /api/report/csv",
            "csv_job":      "GET /api/report/csv/{job_id}",
        },
    }

@app.get("/health")
def health():
    return {"status": "healthy", "redis_connected": redis_manager is not None}


# =============================================================================
# ZIP ANALYSIS — async background job (replaces the old synchronous endpoint)
#
# The old /api/analyze/zip blocked for the full analysis duration (10-30 min
# for a class ZIP), causing backend and frontend timeouts.
#
# Now it works exactly like /api/analyze/assignment:
#   1. Upload + extract ZIP  (fast, happens in the request handler)
#   2. Return job_id immediately
#   3. Run pair comparison in a background thread
#   4. Frontend polls /api/analyze/results/{job_id} for progress
# =============================================================================

def _process_zip_job(job_id: str, mode: str, data: Any) -> None:
    """
    Background worker for ZIP analysis.
    Supports both "project" mode (flat list of files) and "class" mode
    (dict of student_name -> [file_paths]).
    """
    try:
        if mode == "project":
            all_files = data.get("project", [])
            n = len(all_files)
            total_pairs = n * (n - 1) // 2

            job = get_job(job_id)
            job["total_pairs"] = total_pairs
            save_job(job_id, job)

            clone_pairs = []
            done = 0
            for i in range(n):
                for j in range(i + 1, n):
                    try:
                        pr = analyzer._analyze_pair(all_files[i], all_files[j], include_details=False)
                        effective = max(pr.type1_score, pr.type2_score, pr.structural.score, pr.semantic.score)
                        if effective >= 0.25 and pr.primary_clone_type != "none":
                            clone_pairs.append({
                                "file_a":             pr.file_a,
                                "file_b":             pr.file_b,
                                "type1_score":        pr.type1_score,
                                "type2_score":        pr.type2_score,
                                "structural_score":   pr.structural.score,
                                "semantic_score":     pr.semantic.score,
                                "effective_score":    round(effective, 4),
                                "primary_clone_type": pr.primary_clone_type,
                                "similarity_level":   pr.similarity_level,
                                "needs_review":       pr.needs_review,
                                "summary":            pr.summary,
                            })
                    except Exception as e:
                        logger.warning(f"[Job {job_id}] Pair error: {e}")
                    finally:
                        done += 1
                        # Update progress every 50 pairs
                        if done % 50 == 0 or done == total_pairs:
                            job = get_job(job_id)
                            job["analyzed_count"] = done
                            job["progress"]       = round(done / max(total_pairs, 1) * 100, 1)
                            job["clone_pairs"]    = clone_pairs
                            job["results"]        = clone_pairs
                            job["updated_at"]     = time.time()
                            save_job(job_id, job)

            job = get_job(job_id)
            job.update({
                "status":        "completed",
                "analyzed_count": done,
                "progress":      100.0,
                "clone_pairs":   clone_pairs,
                "results":       clone_pairs,
                "updated_at":    time.time(),
            })
            save_job(job_id, job)
            logger.info(f"[Job {job_id}] project mode done — {len(clone_pairs)} pairs from {done} comparisons")

        else:
            # class mode: data is dict of { student_name: [file_paths] }
            students = list(data.items())
            n = len(students)
            student_names = {}

            # Build all cross-student file pairs upfront so we can track total accurately
            all_pairs = []
            for i, (name_i, files_i) in enumerate(students):
                student_names[str(i + 1)] = name_i
                for j in range(i + 1, n):
                    name_j, files_j = students[j]
                    for fa in files_i:
                        for fb in files_j:
                            all_pairs.append((i + 1, name_i, fa, j + 1, name_j, fb))

            total_pairs = len(all_pairs)
            job = get_job(job_id)
            job["total_pairs"]  = total_pairs
            job["student_names"] = student_names
            save_job(job_id, job)

            clone_pairs = []
            done = 0
            for (sid_a, name_a, fa, sid_b, name_b, fb) in all_pairs:
                try:
                    pr = analyzer._analyze_pair(fa, fb, include_details=False)
                    effective = max(pr.type1_score, pr.type2_score, pr.structural.score, pr.semantic.score)
                    if effective >= 0.25 and pr.primary_clone_type != "none":
                        clone_pairs.append({
                            "student_a_id":       sid_a,
                            "student_b_id":       sid_b,
                            "student_a_name":     name_a,
                            "student_b_name":     name_b,
                            "file_a":             pr.file_a,
                            "file_b":             pr.file_b,
                            "type1_score":        pr.type1_score,
                            "type2_score":        pr.type2_score,
                            "structural_score":   pr.structural.score,
                            "semantic_score":     pr.semantic.score,
                            "effective_score":    round(effective, 4),
                            "primary_clone_type": pr.primary_clone_type,
                            "similarity_level":   pr.similarity_level,
                            "needs_review":       pr.needs_review,
                            "summary":            pr.summary,
                        })
                except Exception as e:
                    logger.warning(f"[Job {job_id}] Pair error {fa} vs {fb}: {e}")
                finally:
                    done += 1
                    if done % 50 == 0 or done == total_pairs:
                        job = get_job(job_id)
                        job["analyzed_count"] = done
                        job["progress"]       = round(done / max(total_pairs, 1) * 100, 1)
                        job["clone_pairs"]    = clone_pairs
                        job["results"]        = clone_pairs
                        job["student_names"]  = student_names
                        job["updated_at"]     = time.time()
                        save_job(job_id, job)

            job = get_job(job_id)
            job.update({
                "status":         "completed",
                "analyzed_count": done,
                "progress":       100.0,
                "clone_pairs":    clone_pairs,
                "results":        clone_pairs,
                "student_names":  student_names,
                "updated_at":     time.time(),
            })
            save_job(job_id, job)
            logger.info(f"[Job {job_id}] class mode done — {len(clone_pairs)} pairs from {done} comparisons")

    except Exception as e:
        logger.error(f"[Job {job_id}] fatal error: {e}", exc_info=True)
        job = get_job(job_id)
        if job:
            job["status"] = "failed"
            job["error"]  = str(e)
            save_job(job_id, job)


@app.post("/api/analyze/zip")
async def analyze_zip(file: UploadFile = File(...)):
    """
    Upload a class ZIP and start analysis as a background job.
    Returns job_id immediately — poll /api/analyze/results/{job_id} for progress.
    """
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files accepted")

    job_id  = str(uuid.uuid4())
    zip_dir = UPLOAD_DIR / job_id
    zip_dir.mkdir(exist_ok=True)
    zip_path = zip_dir / (file.filename or "upload.zip")

    try:
        logger.info(f"[Job {job_id}] Saving ZIP: {file.filename}")
        await save_upload(file, zip_path)

        logger.info(f"[Job {job_id}] Extracting ZIP")
        extractor = ZipExtractor()
        mode, data = extractor.extract(str(zip_path))
        logger.info(f"[Job {job_id}] Extraction complete — mode: {mode}")

        # Resolve student count / file count for the initial response
        if mode == "project":
            file_count    = len(data.get("project", []))
            student_count = file_count
        else:
            student_count = len(data)
            file_count    = sum(len(v) for v in data.values())

        if file_count < 2:
            cleanup(zip_dir)
            raise HTTPException(status_code=400, detail="Less than 2 files found in ZIP")

        # Create job and kick off background processing
        job_state = _make_job(job_id)
        job_state["mode"] = mode
        save_job(job_id, job_state)

        loop = asyncio.get_event_loop()
        loop.run_in_executor(executor, _process_zip_job, job_id, mode, data)

        logger.info(f"[Job {job_id}] Background worker started — {student_count} students, {file_count} files")

        return {
            "job_id":         job_id,
            "status":         "processing",
            "mode":           mode,
            "total_students": student_count,
            "total_files":    file_count,
        }

    except HTTPException:
        cleanup(zip_dir)
        raise
    except Exception as e:
        logger.error(f"[Job {job_id}] ZIP setup failed: {e}", exc_info=True)
        cleanup(zip_dir)
        raise HTTPException(status_code=500, detail=f"ZIP processing failed: {str(e)}")


# =============================================================================
# ASSIGNMENT ANALYSIS — cross-student background job
# =============================================================================

def _run_assignment_analysis(job_id: str, request: AssignmentAnalysisRequest) -> None:
    MAX_ROUNDS     = 3
    PAIR_TIMEOUT_S = 60

    job_state = get_job(job_id)
    if not job_state:
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
    skip_pairs    = set()
    all_pair_indices = {(i, j) for i in range(n) for j in range(i + 1, n)}

    for round_num in range(1, MAX_ROUNDS + 1):
        logger.info(f"[Job {job_id}] Round {round_num}/{MAX_ROUNDS}")
        try:
            result = analyzer.analyze_for_assignment(
                student_submissions=submissions,
                language=request.language,
                extension_weights=request.extension_weights or {},
                pair_timeout_seconds=PAIR_TIMEOUT_S,
                skip_pairs=skip_pairs,
                enable_type1=request.enable_type1,
                enable_type2=request.enable_type2,
                enable_type3=request.enable_type3,
                enable_type4=request.enable_type4,
            )
        except Exception as e:
            logger.error(f"[Job {job_id}] Round {round_num} error: {e}")
            job_state = get_job(job_id)
            job_state["status"] = "failed"
            job_state["error"]  = str(e)
            save_job(job_id, job_state)
            return

        job_state    = get_job(job_id)
        new_pairs    = result.get("clone_pairs", [])
        student_names = job_state.get("student_names", {})
        for cp in new_pairs:
            if student_names:
                cp["student_a_name"] = student_names.get(str(cp.get("student_a_id")), "")
                cp["student_b_name"] = student_names.get(str(cp.get("student_b_id")), "")
        all_clone_pairs.extend(new_pairs)

        timed_out  = {tuple(p) for p in result.get("remaining_pairs", [])}
        attempted  = all_pair_indices - skip_pairs
        newly_done = attempted - timed_out
        skip_pairs.update(newly_done)

        job_state.update({
            "analyzed_count":  len(skip_pairs),
            "remaining_count": len(timed_out),
            "clone_pairs":     all_clone_pairs,
            "results":         all_clone_pairs,
            "class_analysis":  result.get("class_analysis", {}),
            "status":          "partial" if timed_out else "completed",
            "progress":        round(len(skip_pairs) / max(total_pairs, 1) * 100, 1),
        })
        save_job(job_id, job_state)

        if not timed_out:
            break

    job_state = get_job(job_id)
    job_state["status"] = "completed"
    save_job(job_id, job_state)
    logger.info(f"[Job {job_id}] done — {job_state['analyzed_count']}/{total_pairs} pairs, "
                f"{len(all_clone_pairs)} clone pairs")


@app.post("/api/analyze/assignment")
async def analyze_assignment(
    request: AssignmentAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    """Kick off cross-student assignment analysis. Returns job_id for polling."""
    if len(request.submissions) < 2:
        raise HTTPException(status_code=400, detail="At least 2 student submissions required")

    missing = [fp for sub in request.submissions for fp in sub.files if not Path(fp).exists()]
    if missing:
        raise HTTPException(status_code=400, detail=f"File(s) not found: {missing[:5]}")

    job_id    = str(uuid.uuid4())
    job_state = {
        "status":          "processing",
        "assignment_id":   request.assignment_id,
        "analyzed_count":  0,
        "total_pairs":     0,
        "remaining_count": 0,
        "progress":        0.0,
        "clone_pairs":     [],
        "results":         [],
        "class_analysis":  {},
        "error":           None,
        "created_at":      time.time(),
    }
    save_job(job_id, job_state)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_assignment_analysis, job_id, request)

    return {
        "job_id":         job_id,
        "status":         "processing",
        "assignment_id":  request.assignment_id,
        "total_students": len(request.submissions),
    }


# =============================================================================
# POLL ENDPOINT — normalises field names for both job types
# =============================================================================

@app.get("/api/analyze/results/{job_id}")
def get_job_results(job_id: str):
    """Poll job status. Compatible with both ZIP and assignment analysis jobs."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    total_pairs     = job.get("total_pairs", 0)
    analyzed_count  = job.get("analyzed_count", 0)
    progress_val    = job.get("progress", 0.0)
    clone_pairs_val = job.get("clone_pairs", job.get("all_clone_pairs", []))

    return {
        "job_id":          job_id,
        "status":          job.get("status", "unknown"),
        "assignment_id":   job.get("assignment_id"),
        "progress":        progress_val,
        "progress_percent": progress_val,
        "analyzed_count":  analyzed_count,
        "total_pairs":     total_pairs,
        "remaining_count": job.get("remaining_count", 0),
        "clone_pairs":     clone_pairs_val,
        "results":         clone_pairs_val,
        "class_analysis":  job.get("class_analysis", {}),
        "error":           job.get("error"),
        "mode":            job.get("mode", "unknown"),
        "student_names":   job.get("student_names", {}),
        "created_at":      job.get("created_at"),
        "updated_at":      job.get("updated_at"),
    }


# =============================================================================
# DIRECT FILE ANALYSIS (small batches, < 30 files)
# =============================================================================

@app.post("/api/analyze/detailed")
async def analyze_detailed(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")
    if len(files) > 30:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files ({len(files)}) for synchronous analysis. Max is 30 — use a ZIP instead."
        )

    job_id  = f"detailed_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths  = await save_files(files, job_id)
        report = analyzer.analyze(paths, detailed=True)
        return {"status": "success", "mode": "detailed", "total_files": len(paths), **report}
    except Exception as e:
        logger.error(f"Detailed analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        cleanup(job_dir)

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


# =============================================================================
# CSV REPORT ENDPOINTS
# =============================================================================

@app.post("/api/report/csv")
async def generate_csv_from_files(
    files: List[UploadFile] = File(...),
    assignment_id: str = "",
    language: str = "cpp",
    mode: str = "summary",
):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required")

    job_id  = f"csv_{int(time.time())}"
    job_dir = UPLOAD_DIR / job_id
    try:
        paths      = await save_files(files, job_id)
        report     = analyzer.analyze(paths, detailed=True)
        report_gen = ReportGenerator()
        csv_str    = report_gen.from_analysis_response(
            report, assignment_id=assignment_id, language=language, mode=mode, detailed=True,
        )
        filename = f"codespectra_{mode}_{assignment_id or 'analysis'}_{int(time.time())}.csv"
        return StreamingResponse(
            io.StringIO(csv_str),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"CSV generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")
    finally:
        cleanup(job_dir)

@app.get("/api/report/csv/{job_id}")
async def generate_csv_from_job(
    job_id: str,
    assignment_id: str = "",
    language: str = "cpp",
):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job["status"] not in ("completed", "partial"):
        raise HTTPException(status_code=400, detail=f"Job not yet complete (status={job['status']})")

    clone_pairs = job.get("clone_pairs") or job.get("all_clone_pairs") or []
    report_gen  = ReportGenerator()
    csv_str     = report_gen.from_clone_pairs(
        clone_pairs,
        assignment_id=assignment_id or str(job.get("assignment_id", "")),
        language=language,
    )
    filename = f"codespectra_report_{assignment_id or job_id}_{int(time.time())}.csv"
    return StreamingResponse(
        io.StringIO(csv_str),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.delete("/api/analyze/job/{job_id}")
def cleanup_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    for key in ("pairs", "students"):
        job.pop(key, None)
    save_job(job_id, job)
    return {"message": f"Job {job_id} cleaned up"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
