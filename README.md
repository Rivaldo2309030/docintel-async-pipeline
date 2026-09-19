# U1T02: Document Intelligence Asynchronous Pipeline

An enterprise-grade asynchronous document intelligence platform designed to ingest raw business documents (PDF, PNG, JPG/JPEG, TXT), decouple heavy extraction workflows via the **Claim-Check Pattern**, queue execution with **Celery & Redis**, parse text and metadata using multi-engine Document Intelligence strategies, and track lifecycle state in **PostgreSQL**.

---

## 🌟 Key Architecture & Features

1. **Claim-Check Pattern**: Large payload files are stored directly in isolated storage (`storage_data/`). The API returns a lightweight `claim_check_id` immediately, decoupling payload size from network queue broker traffic.
2. **Multi-Engine Document Intelligence**:
   - **PDF**: PyMuPDF (`fitz`) native vector extraction with automatic fallback to **PyTesseract OCR** for scanned/image-only PDFs.
   - **Images (PNG/JPG/JPEG)**: Pillow contrast preprocessing + PyTesseract OCR.
   - **Plain Text (TXT)**: Auto-encoding detection using `chardet`.
   - **Benchmark Suite**: Empirical comparison module evaluating PyPDF, PyMuPDF, pdfplumber, and Tesseract.
3. **Resilience & Fault Tolerance**:
   - Late worker acknowledgments (`acks_late=True`) to prevent task loss during worker restarts.
   - Corrupted file detection and non-terminal error state tracking.
   - Exponential retry backoff on transient storage/network issues.
4. **Monitoring & Web UI**:
   - Interactive glassmorphic web dashboard at `http://localhost:8000/`.
   - Real-time queue monitoring via **Celery Flower** at `http://localhost:5555/`.
5. **IEEE LaTeX Report**:
   - Complete report ready for compilation on **Overleaf** under `report/report.tex`.

---

## 🚀 Quickstart (Docker Compose)

Launch the entire stack (PostgreSQL, Redis, FastAPI, Celery Worker, Flower, and Web UI) with a single command:

```bash
docker compose up --build
```

### Access Services:
- **Web UI & OpenAPI Docs**: [http://localhost:8000](http://localhost:8000)
- **Celery Flower Dashboard**: [http://localhost:5555](http://localhost:5555)
- **PostgreSQL Database**: `localhost:5432` (`db: docintel`, `user: postgres`, `pass: postgrespassword`)

---

## 📁 Project Structure

```
.
├── docker-compose.yml       # Full stack orchestration
├── README.md                # Project documentation
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI workflow
├── report/
│   └── report.tex          # IEEE LaTeX Report (English) formatted for Overleaf
├── backend/
│   ├── Dockerfile           # Backend container with Tesseract OCR & dependencies
│   ├── requirements.txt     # Python dependencies
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment & pipeline settings
│   ├── database/            # SQLAlchemy models & session handling
│   ├── storage/             # Claim-Check pattern storage implementation
│   ├── parsers/             # PDF, Image, TXT, and Benchmark intelligence engines
│   ├── tasks/               # Celery app & async document parsing tasks
│   └── routers/             # Ingestion & Job Tracking endpoints
├── frontend/
│   ├── index.html           # Web UI layout
│   ├── style.css            # Modern glassmorphic styles
│   └── app.js               # Frontend polling & upload client
└── tests/
    ├── test_ingestion.py    # Unit tests for API endpoints
    └── test_parsers.py      # Unit tests for document parsers
```

---

## 🧪 Running Unit Tests Locally

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run pytest suite
pytest tests/ -v
```

---

## 📄 IEEE LaTeX Report (Overleaf)

The report deliverable is located at [`report/report.tex`](file:///c:/Users/Rivaldo/Documents/DEXTER/Tarea%202/report/report.tex). It is written in English and follows the official `IEEEtran` document class format matching `dexter report format.tex`. You can directly upload the contents of the `report/` directory to **Overleaf** to compile the PDF.
