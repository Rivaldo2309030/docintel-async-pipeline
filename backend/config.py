import os
import tempfile

def get_default_storage_dir() -> str:
    env_dir = os.getenv("STORAGE_DIR")
    if env_dir:
        return env_dir
    if os.path.exists("/app") and os.access("/app", os.W_OK):
        return "/app/storage_data"
    return os.path.join(tempfile.gettempdir(), "docintel_storage_data")

class Settings:
    PROJECT_NAME: str = "Document Intelligence Pipeline"
    API_V1_STR: str = "/api"
    
    # Storage settings (Claim-Check pattern)
    STORAGE_DIR: str = get_default_storage_dir()
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB upload limit
    
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
    ALLOWED_MIME_TYPES: set = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "text/plain"
    }

    # PostgreSQL Connection
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "docintel")

    @property
    def DATABASE_URL(self) -> str:
        if os.getenv("TESTING", "False").lower() in ("true", "1"):
            return "sqlite:///./test.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis & Celery Config
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

settings = Settings()
