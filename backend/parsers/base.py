from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseDocumentParser(ABC):
    """Abstract Base Class for Document Parsers."""
    
    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parses raw file bytes.
        Returns:
            Tuple[extracted_text (str), metadata (dict)]
        """
        pass
