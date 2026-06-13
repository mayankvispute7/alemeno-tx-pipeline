import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Job, Transaction, JobSummary
from app.schemas.payload import JobCreateResponse, JobStatusResponse, JobResultsResponse, JobListItem
from app.worker.tasks import process_transaction_file

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. UPLOAD ENDPOINT
# ---------------------------------------------------------
@router.post("/jobs/upload", response_model=JobCreateResponse)
def upload_transactions_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_job = Job(filename=file.filename, status="pending")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    process_transaction_file.delay(new_job.id, file_path)

    return JobCreateResponse(
        job_id=new_job.id,
        message="File uploaded successfully. Job is pending.",
        filename=file.filename
    )

# ---------------------------------------------------------
# 2. LIST JOBS ENDPOINT
# ---------------------------------------------------------
@router.get("/jobs", response_model=List[JobListItem])
def list_jobs(status: Optional[str] = Query(None, description="Filter by status"), db: Session = Depends(get_db)):
    """List all jobs. Optionally filter by status (e.g., ?status=completed)."""
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status.lower())
    
    jobs = query.order_by(Job.created_at.desc()).all()
    
    # Map database models to our Pydantic response schema
    return [
        JobListItem(
            job_id=job.id,
            filename=job.filename,
            status=job.status,
            row_count_clean=job.row_count_clean,
            created_at=job.created_at
        ) for job in jobs
    ]

# ---------------------------------------------------------
# 3. GET JOB STATUS
# ---------------------------------------------------------
@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Return the current status of a job. Includes high-level stats if completed."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    summary_stats = None
    if job.status == "completed":
        summary = db.query(JobSummary).filter(JobSummary.job_id == job_id).first()
        if summary:
            summary_stats = {
                "total_spend_inr": summary.total_spend_inr,
                "total_spend_usd": summary.total_spend_usd,
                "anomaly_count": summary.anomaly_count
            }

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        filename=job.filename,
        summary_stats=summary_stats
    )

# ---------------------------------------------------------
# 4. GET FULL RESULTS
# ---------------------------------------------------------
@router.get("/jobs/{job_id}/results", response_model=JobResultsResponse)
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    """Return the full structured output: transactions, anomalies, and AI narrative."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Results not available. Job is currently '{job.status}'")

    transactions = db.query(Transaction).filter(Transaction.job_id == job_id).all()
    summary = db.query(JobSummary).filter(JobSummary.job_id == job_id).first()

    return JobResultsResponse(
        job_id=job.id,
        status=job.status,
        filename=job.filename,
        summary=summary,
        transactions=transactions
    )