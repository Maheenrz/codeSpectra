# analysis-engine/utils/queue_manager.py
import asyncio
import uuid
import json
import redis
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QueueManager")

# Initialize Redis client
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class AnalysisQueueManager:
    def __init__(self):
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.max_concurrent_jobs = 2  # Limits CPU thrashing during Type-4
        self.worker_tasks = []

    def _save_job(self, job_data: dict):
        """Persist job state to Redis with 24h expiry"""
        job_id = job_data['job_id']
        try:
            # Helper to make results JSON serializable (converts Paths to strings)
            serialized_data = json.dumps(job_data, default=str)
            redis_client.set(f"job:{job_id}", serialized_data, ex=86400)
        except Exception as e:
            logger.error(f"Failed to save job {job_id} to Redis: {e}")

    def _load_job(self, job_id: str) -> Optional[dict]:
        """Retrieve job state from Redis"""
        data = redis_client.get(f"job:{job_id}")
        return json.loads(data) if data else None

    async def submit_job(self, assignment_id: int, pairs: List[Dict]) -> str:
        """Create a new job and push it to the processing queue"""
        job_id = str(uuid.uuid4())
        job_data = {
            'job_id': job_id,
            'assignment_id': assignment_id,
            'pairs': pairs,
            'total_pairs': len(pairs),
            'completed_pairs': 0,
            'failed_pairs': 0,
            'status': "pending",
            'results': [],
            'errors': [],
            'started_at': None,
            'completed_at': None,
            'progress': 0.0
        }
        self._save_job(job_data)
        await self.processing_queue.put(job_id)
        logger.info(f"Job {job_id} submitted for assignment {assignment_id}")
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Public API to poll job status"""
        return self._load_job(job_id)

    async def start_workers(self):
        """Initialize the worker pool"""
        for i in range(self.max_concurrent_jobs):
            task = asyncio.create_task(self._worker(i))
            self.worker_tasks.append(task)
        logger.info(f"Started {self.max_concurrent_jobs} analysis workers")

    async def _worker(self, worker_id: int):
        """Background worker that pulls jobs from the queue"""
        # Lazy imports to prevent circular dependencies
        from engine.analyzer import CloneAnalyzer, AnalyzerConfig
        
        # Initialize analyzer with standard educational config
        config = AnalyzerConfig()
        analyzer = CloneAnalyzer(config)

        while True:
            job_id = await self.processing_queue.get()
            job = self._load_job(job_id)
            
            if not job:
                self.processing_queue.task_done()
                continue

            logger.info(f"Worker-{worker_id} starting job {job_id}")
            job['status'] = "processing"
            job['started_at'] = datetime.now().isoformat()
            self._save_job(job)

            for i, pair in enumerate(job['pairs']):
                try:
                    # Threading used because Type-4/Joern/Compilation are CPU heavy 
                    # and would otherwise block the entire FastAPI event loop.
                    # We call analyze_for_assignment which is the correct entry point in v3.0
                    result = await asyncio.to_thread(
                        analyzer.analyze_for_assignment,
                        pair['files_a'],
                        pair['files_b']
                    )
                    
                    if result:
                        job['results'].append(result)
                    
                    job['completed_pairs'] += 1
                except Exception as e:
                    logger.error(f"Error in job {job_id} pair {i}: {e}")
                    job['failed_pairs'] += 1
                    job['errors'].append({"pair": i, "error": str(e)})
                
                # Update progress incrementally
                job['progress'] = round((job['completed_pairs'] / job['total_pairs']) * 100, 2)
                self._save_job(job)

            job['status'] = "completed"
            job['completed_at'] = datetime.now().isoformat()
            job['progress'] = 100.0
            self._save_job(job)
            
            logger.info(f"Worker-{worker_id} finished job {job_id}")
            self.processing_queue.task_done()