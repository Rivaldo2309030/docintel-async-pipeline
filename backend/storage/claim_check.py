import os
import uuid
from typing import Tuple
from config import settings

class ClaimCheckStore:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or settings.STORAGE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save_payload(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Saves raw file content and returns (claim_check_id, storage_path).
        Claim-Check pattern: Large payload is stored offline, small ID is returned.
        """
        claim_check_id = str(uuid.uuid4())
        safe_filename = "".join([c for c in original_filename if c.isalnum() or c in (".", "_", "-")])
        stored_name = f"{claim_check_id}_{safe_filename}"
        storage_path = os.path.join(self.base_dir, stored_name)

        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        return claim_check_id, storage_path

    def read_payload(self, storage_path: str) -> bytes:
        """Reads and returns stored raw payload."""
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"Claim check payload not found at {storage_path}")
        with open(storage_path, "rb") as f:
            return f.read()

    def delete_payload(self, storage_path: str) -> bool:
        """Removes payload after processing or cleanup."""
        if os.path.exists(storage_path):
            os.remove(storage_path)
            return True
        return False

claim_check_store = ClaimCheckStore()
