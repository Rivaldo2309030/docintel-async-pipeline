from datetime import datetime, timezone
import os
import traceback
from tasks.celery_app import celery_app
from database.session import SessionLocal
from database.models import Job
from storage.claim_check import claim_check_store
from parsers.pdf_parser import PDFDocumentParser
from parsers.image_parser import ImageDocumentParser
from parsers.txt_parser import TextDocumentParser

@celery_app.task(name="tasks.document_tasks.process_document_job", bind=True, max_retries=2, default_retry_delay=5)
def process_document_job(self, job_id: str):
    """
    Asynchronous worker task that parses a document from Claim-Check storage.
    Updates PostgreSQL lifecycle state: QUEUED -> PROCESSING -> COMPLETED / FAILED.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"status": "error", "message": f"Job {job_id} not found in database"}

        # Update status to PROCESSING
        job.status = "PROCESSING"
        job.progress = 25.0
        db.commit()

        # Retrieve payload via Claim-Check pattern
        try:
            file_bytes = claim_check_store.read_payload(job.storage_path)
        except FileNotFoundError as e:
            job.status = "FAILED"
            job.error_message = f"Storage payload error: {str(e)}"
            db.commit()
            return {"status": "failed", "error": str(e)}

        job.progress = 50.0
        db.commit()

        # Select parser strategy based on format
        fmt = job.file_format.lower()
        if fmt == "pdf":
            parser = PDFDocumentParser()
        elif fmt in ("png", "jpg", "jpeg"):
            parser = ImageDocumentParser()
        elif fmt == "txt":
            parser = TextDocumentParser()
        else:
            raise ValueError(f"Unsupported document format: {job.file_format}")

        # Execute Document Intelligence parsing
        extracted_text, metadata = parser.parse(file_bytes, job.filename)

        # Update job with results
        job.extracted_text = extracted_text
        job.metadata_json = metadata
        job.parser_used = metadata.get("parser_engine", "Default Parser")
        job.progress = 100.0
        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)

        db.commit()
        return {"status": "completed", "job_id": job_id, "parser": job.parser_used}

    except Exception as exc:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = f"Processing Exception: {str(exc)}\n{traceback.format_exc()}"
            job.progress = 0.0
            db.commit()

        # Retry transient exceptions if applicable
        if self.request.retries < self.max_retries and not isinstance(exc, (ValueError, FileNotFoundError)):
            raise self.retry(exc=exc)

        return {"status": "failed", "job_id": job_id, "error": str(exc)}

    finally:
        db.close()
