import asyncio
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class AnalysisJob:
    """Represents a single analysis job"""
    job_id: str
    assignment_id: int
    pairs: List[Dict]  # List of {student_a_id, student_b_id, files_a, files_b, question_id}
    total_pairs: int
    completed_pairs: int = 0
    failed_pairs: int = 0
    status: str = "pending"  # pending, processing, partial, completed, failed
    results: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int = 900  # 15 minutes
    
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_pairs == 0:
            return 0
        return (self.completed_pairs / self.total_pairs) * 100
    
    def is_timeout(self) -> bool:
        """Check if job has timed out"""
        if not self.started_at:
            return False
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed > self.timeout_seconds
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'job_id': self.job_id,
            'assignment_id': self.assignment_id,
            'total_pairs': self.total_pairs,
            'completed_pairs': self.completed_pairs,
            'failed_pairs': self.failed_pairs,
            'status': self.status,
            'progress': self.progress_percentage(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'results_count': len(self.results),
            'errors_count': len(self.errors)
        }


class AnalysisQueueManager:
    """
    Manages analysis jobs with queue-based retry system
    Handles partial results and timeout recovery
    """
    
    def __init__(self):
        self.jobs: Dict[str, AnalysisJob] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.max_concurrent_jobs = 3
        self.worker_tasks = []
    
    async def start_workers(self):
        """Start background worker tasks"""
        for i in range(self.max_concurrent_jobs):
            task = asyncio.create_task(self._worker(i))
            self.worker_tasks.append(task)
    
    async def stop_workers(self):
        """Stop all workers"""
        for task in self.worker_tasks:
            task.cancel()
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
    
    async def submit_job(self, assignment_id: int, pairs: List[Dict]) -> str:
        """
        Submit a new analysis job
        Returns job_id for tracking
        """
        import uuid
        
        job_id = str(uuid.uuid4())
        job = AnalysisJob(
            job_id=job_id,
            assignment_id=assignment_id,
            pairs=pairs,
            total_pairs=len(pairs)
        )
        
        self.jobs[job_id] = job
        await self.processing_queue.put(job_id)
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        return job.to_dict()
    
    async def get_job_results(self, job_id: str) -> Optional[Dict]:
        """Get job results (including partial results)"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            **job.to_dict(),
            'results': job.results,
            'errors': job.errors
        }
    
    async def _worker(self, worker_id: int):
        """Background worker that processes jobs"""
        print(f"Worker {worker_id} started")
        
        while True:
            try:
                # Get next job from queue
                job_id = await self.processing_queue.get()
                job = self.jobs.get(job_id)
                
                if not job:
                    continue
                
                print(f"Worker {worker_id} processing job {job_id}")
                
                # Mark as processing
                job.status = "processing"
                job.started_at = datetime.now()
                
                # Process job
                await self._process_job(job)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except asyncio.CancelledError:
                print(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    async def _process_job(self, job: AnalysisJob):
        """Process a single job"""
        from .analyzer import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        # Process each pair
        for i, pair in enumerate(job.pairs):
            # Check timeout
            if job.is_timeout():
                print(f"Job {job.job_id} timed out after {job.timeout_seconds}s")
                job.status = "partial"
                
                # Re-queue remaining pairs
                remaining_pairs = job.pairs[i:]
                if remaining_pairs:
                    print(f"Re-queuing {len(remaining_pairs)} remaining pairs")
                    new_job_id = await self.submit_job(job.assignment_id, remaining_pairs)
                    job.errors.append({
                        'type': 'timeout',
                        'message': f'Timeout after {job.completed_pairs} pairs. Remaining queued as job {new_job_id}'
                    })
                
                break
            
            try:
                # Analyze pair
                result = await asyncio.to_thread(
                    analyzer.compare_submissions,
                    pair['files_a'],
                    pair['files_b'],
                    pair.get('question_id')
                )
                
                # Add metadata
                result['student_a_id'] = pair['student_a_id']
                result['student_b_id'] = pair['student_b_id']
                result['question_id'] = pair.get('question_id')
                
                job.results.append(result)
                job.completed_pairs += 1
                
            except Exception as e:
                print(f"Error processing pair: {e}")
                job.failed_pairs += 1
                job.errors.append({
                    'pair_index': i,
                    'student_a_id': pair['student_a_id'],
                    'student_b_id': pair['student_b_id'],
                    'error': str(e)
                })
        
        # Update final status
        if job.completed_pairs == job.total_pairs:
            job.status = "completed"
        elif job.completed_pairs > 0:
            job.status = "partial"
        else:
            job.status = "failed"
        
        job.completed_at = datetime.now()
        
        print(f"Job {job.job_id} finished: {job.status}, {job.completed_pairs}/{job.total_pairs} pairs")


# Global queue manager instance
queue_manager = AnalysisQueueManager()