from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from database.session import get_db
from database.models import Job
from storage.claim_check import claim_check_store

router = APIRouter(prefix="/jobs", tags=["Job Tracking"])

@router.get("", response_model=List[dict])
def list_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Lists document processing jobs with optional status filter and pagination."""
    query = db.query(Job)
    if status_filter:
        query = query.filter(Job.status == status_filter.upper())
    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    return [job.to_dict() for job in jobs]

@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Retrieves detailed status, progress, metadata, and error details for a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found."
        )
    return job.to_dict()

@router.get("/{job_id}/result")
def get_job_result(job_id: str, db: Session = Depends(get_db)):
    """Returns the full extracted plain text content of a completed job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found."
        )
    
    if job.status == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job failed with error: {job.error_message}"
        )
        
    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is currently in '{job.status}' state (progress: {job.progress}%)."
        )

    return Response(
        content=job.extracted_text or "",
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{job.filename}_extracted.txt"'
        }
    )

@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Deletes job record from database and cleans up Claim-Check payload storage."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found."
        )
    
    # Remove payload file from Claim-Check storage
    claim_check_store.delete_payload(job.storage_path)

    db.delete(job)
    db.commit()

    return {"message": f"Job '{job_id}' and storage payload removed successfully."}
