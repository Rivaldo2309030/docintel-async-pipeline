from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, func
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_format = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    
    # Claim-check pattern metadata
    claim_check_id = Column(String(36), nullable=False, unique=True)
    storage_path = Column(String(512), nullable=False)
    
    # Lifecycle & Status
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, PROCESSING, COMPLETED, FAILED
    progress = Column(Float, nullable=False, default=0.0)
    
    # Intelligence Output
    parser_used = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    # Failure handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
            "claim_check_id": self.claim_check_id,
            "status": self.status,
            "progress": self.progress,
            "parser_used": self.parser_used,
            "extracted_text": self.extracted_text,
            "metadata_json": self.metadata_json,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
