from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Field tanpa nilai default wajib ada di .env (seperti DATABASE_URL)
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Field dengan nilai default akan dioverwrite jika ada di .env
    APP_NAME: str = "Similarity Detection System"
    DEBUG: bool = True
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    UPLOAD_DIR: str = "/app/uploads"
    TEMP_DIR: str = "/app/temp"
    MAX_UPLOAD_SIZE: int = 100
    
    MIN_MATCH_LENGTH: int = 10
    K_GRAM: int = 3
    WINDOW_SIZE: int = 4
    
    SBERT_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

    class Config:
        # Pydantic akan mencari file .env
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()