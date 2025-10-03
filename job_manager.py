import json
import os
from datetime import datetime
from logger import get_logger

logger = get_logger(__name__)

# In-memory job store (use Redis in production)
jobs = {}

class JobStatus:
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobStage:
    NEWS_FETCH = "News Fetch"
    SCRIPT_GEN = "Script Generation"
    QUESTION_GEN = "Question Generation"
    TTS_GEN = "TTS Generation"
    PACKAGING = "Packaging"

def create_job(job_id, user_data):
    """Create a new job."""
    jobs[job_id] = {
        "id": job_id,
        "status": JobStatus.QUEUED,
        "progress": 0,
        "stage": None,
        "eta_seconds": None,
        "created_at": datetime.utcnow().isoformat(),
        "user_data": user_data,
        "result": None,
        "error": None
    }
    logger.info(f"Created job {job_id}")
    return jobs[job_id]

def update_job(job_id, status=None, progress=None, stage=None, eta_seconds=None, result=None, error=None):
    """Update job status."""
    if job_id not in jobs:
        logger.error(f"Job {job_id} not found")
        return None
    
    if status:
        jobs[job_id]["status"] = status
    if progress is not None:
        jobs[job_id]["progress"] = progress
    if stage:
        jobs[job_id]["stage"] = stage
    if eta_seconds is not None:
        jobs[job_id]["eta_seconds"] = eta_seconds
    if result:
        jobs[job_id]["result"] = result
    if error:
        jobs[job_id]["error"] = error
    
    logger.debug(f"Updated job {job_id}: status={status}, progress={progress}, stage={stage}")
    return jobs[job_id]

def get_job(job_id):
    """Get job status."""
    return jobs.get(job_id)

def get_job_result(job_id):
    """Get job result if completed."""
    job = jobs.get(job_id)
    if job and job["status"] == JobStatus.COMPLETED:
        return job["result"]
    return None
