from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from config import settings
from database.session import init_db
from routers import ingestion, tracking

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Document Intelligence Asynchronous Pipeline using FastAPI, Celery, Redis, and PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize DB tables
@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print(f"Database init warning: {str(e)}")

# Include API Routers
app.include_router(ingestion.router, prefix=settings.API_V1_STR)
app.include_router(tracking.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "storage_dir": settings.STORAGE_DIR
    }

# Serve static frontend files if directory exists
possible_frontend_dirs = [
    "/app/frontend",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")),
]
frontend_dir = next((d for d in possible_frontend_dirs if os.path.exists(d)), None)

if frontend_dir:
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

