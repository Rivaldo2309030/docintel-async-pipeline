import fitz  # PyMuPDF
import io
from PIL import Image
import pytesseract
from typing import Dict, Any, Tuple
from parsers.base import BaseDocumentParser

class PDFDocumentParser(BaseDocumentParser):
    def parse(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)
        full_text = []
        ocr_pages_count = 0
        total_word_count = 0

        for page_num in range(page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text").strip()
            
            # Check if page is scanned / image-only (less than 10 words extracted natively)
            words = page_text.split()
            if len(words) < 10:
                # Render page to image at 300 DPI for OCR fallback
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                if len(ocr_text.strip()) > len(page_text):
                    page_text = ocr_text.strip()
                    ocr_pages_count += 1

            full_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            total_word_count += len(page_text.split())

        extracted_content = "\n\n".join(full_text)
        
        metadata = {
            "page_count": page_count,
            "total_word_count": total_word_count,
            "ocr_fallback_pages": ocr_pages_count,
            "is_scanned": ocr_pages_count > 0,
            "parser_engine": "PyMuPDF (fitz) + Tesseract OCR Fallback"
        }

        return extracted_content, metadata
