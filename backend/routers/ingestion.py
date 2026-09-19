from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
import os
from typing import Optional
from config import settings
from database.session import get_db
from database.models import Job
from storage.claim_check import claim_check_store
from tasks.document_tasks import process_document_job
from parsers.benchmark import run_pdf_parser_benchmark

router = APIRouter(prefix="/documents", tags=["Ingestion"])

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest document endpoint using Claim-Check Architecture:
    1. Validates file extension and upload size limits.
    2. Stores payload in Claim-Check storage.
    3. Creates Job record in DB with QUEUED status.
    4. Dispatches asynchronous Celery task and returns claim check ID immediately.
    """
    filename = file.filename or "unnamed_document"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {sorted(list(settings.ALLOWED_EXTENSIONS))}"
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    # 1. Claim-Check Storage
    claim_check_id, storage_path = claim_check_store.save_payload(file_bytes, filename)

    # 2. Database Job Creation
    job = Job(
        filename=filename,
        file_format=ext.replace(".", ""),
        file_size_bytes=file_size,
        claim_check_id=claim_check_id,
        storage_path=storage_path,
        status="QUEUED",
        progress=0.0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 3. Async Queue Dispatch (Celery + Redis)
    try:
        process_document_job.delay(job.id)
    except Exception as exc:
        # Graceful fallback if Redis is unavailable
        job.status = "QUEUED"
        job.error_message = f"Queue Warning: Task enqueued, but broker notification failed: {str(exc)}"
        db.commit()

    return {
        "message": "Document accepted for asynchronous processing",
        "job_id": job.id,
        "claim_check_id": claim_check_id,
        "filename": filename,
        "file_size_bytes": file_size,
        "status": job.status,
        "tracking_url": f"/api/jobs/{job.id}"
    }

@router.post("/benchmark")
async def benchmark_pdf(file: UploadFile = File(...)):
    """Runs empirical benchmark across multiple PDF parsing libraries."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benchmark endpoint requires a PDF file."
        )

    file_bytes = await file.read()
    benchmark_results = run_pdf_parser_benchmark(file_bytes)
    return {
        "filename": filename,
        "benchmark_summary": benchmark_results
    }
