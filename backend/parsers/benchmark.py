import time
import io
import fitz
import pypdf
import pdfplumber
import pytesseract
from PIL import Image
from typing import Dict, Any, List

def run_pdf_parser_benchmark(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Runs an empirical benchmark comparing multiple PDF parsing libraries:
    1. PyMuPDF (fitz)
    2. pypdf
    3. pdfplumber
    4. PyTesseract OCR (rendered pages)
    """
    results = []

    # 1. PyMuPDF (fitz)
    start = time.perf_counter()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pymupdf_text = "".join([page.get_text() for page in doc])
    elapsed_fitz = (time.perf_counter() - start) * 1000  # ms
    results.append({
        "engine": "PyMuPDF (fitz)",
        "execution_time_ms": round(elapsed_fitz, 2),
        "word_count": len(pymupdf_text.split()),
        "status": "Success",
        "notes": "Native vector & font parsing; fastest throughput"
    })

    # 2. pypdf
    start = time.perf_counter()
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pypdf_text = "".join([page.extract_text() or "" for page in reader.pages])
        elapsed_pypdf = (time.perf_counter() - start) * 1000
        results.append({
            "engine": "pypdf",
            "execution_time_ms": round(elapsed_pypdf, 2),
            "word_count": len(pypdf_text.split()),
            "status": "Success",
            "notes": "Pure Python implementation; lightweight but slower on large files"
        })
    except Exception as e:
        results.append({"engine": "pypdf", "status": f"Failed: {str(e)}"})

    # 3. pdfplumber
    start = time.perf_counter()
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            plumber_text = "".join([page.extract_text() or "" for page in pdf.pages])
        elapsed_plumber = (time.perf_counter() - start) * 1000
        results.append({
            "engine": "pdfplumber",
            "execution_time_ms": round(elapsed_plumber, 2),
            "word_count": len(plumber_text.split()),
            "status": "Success",
            "notes": "Detailed layout structure & tables extraction; high memory overhead"
        })
    except Exception as e:
        results.append({"engine": "pdfplumber", "status": f"Failed: {str(e)}"})

    # 4. PyTesseract OCR (first page sample)
    start = time.perf_counter()
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) > 0:
            pix = doc[0].get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img)
            elapsed_ocr = (time.perf_counter() - start) * 1000
            results.append({
                "engine": "PyTesseract OCR (Page 1)",
                "execution_time_ms": round(elapsed_ocr, 2),
                "word_count": len(ocr_text.split()),
                "status": "Success",
                "notes": "Pixel/vision layout recognition; compute intensive (fallback only)"
            })
    except Exception as e:
        results.append({"engine": "PyTesseract OCR", "status": f"Failed: {str(e)}"})

    return results
