import chardet
from typing import Dict, Any, Tuple
from parsers.base import BaseDocumentParser

class TextDocumentParser(BaseDocumentParser):
    def parse(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        # Auto-detect encoding
        detection = chardet.detect(file_bytes)
        encoding = detection.get("encoding") or "utf-8"
        confidence = detection.get("confidence") or 0.0

        try:
            extracted_text = file_bytes.decode(encoding)
        except Exception:
            # Fallback to utf-8 with replacement for invalid bytes
            extracted_text = file_bytes.decode("utf-8", errors="replace")
            encoding = "utf-8 (fallback)"

        lines = extracted_text.splitlines()
        line_count = len(lines)
        word_count = len(extracted_text.split())

        metadata = {
            "detected_encoding": encoding,
            "encoding_confidence": round(confidence, 2),
            "line_count": line_count,
            "word_count": word_count,
            "parser_engine": f"Chardet Auto-Encoding ({encoding}) + Native Text Decoding"
        }

        return extracted_text.strip(), metadata
