import io
from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from typing import Dict, Any, Tuple
from parsers.base import BaseDocumentParser

class ImageDocumentParser(BaseDocumentParser):
    def parse(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        format_name = img.format or "UNKNOWN"
        mode = img.mode

        # Preprocessing: convert to grayscale and auto-contrast for higher OCR precision
        gray_img = ImageOps.grayscale(img)
        enhanced_img = ImageEnhance.Contrast(gray_img).enhance(1.5)

        ocr_text = pytesseract.image_to_string(enhanced_img).strip()
        word_count = len(ocr_text.split())

        metadata = {
            "width_px": width,
            "height_px": height,
            "color_mode": mode,
            "image_format": format_name,
            "word_count": word_count,
            "parser_engine": "Tesseract OCR v5 + Pillow Image Preprocessing"
        }

        return ocr_text, metadata
