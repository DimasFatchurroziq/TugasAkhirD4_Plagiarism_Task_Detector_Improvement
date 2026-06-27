from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Field tanpa nilai default wajib ada di .env (seperti DATABASE_URL)
    DB_USER: str = "plagiarism_user"
    DB_PASSWORD: str = "plagiarism_pass"
    DB_NAME: str = "plagiarism_db"
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Field dengan nilai default akan dioverwrite jika ada di .env
    APP_NAME: str = "Similarity Detection System"
    DEBUG: bool = True
    
    UPLOAD_DIR: str = "/app/uploads"
    TEMP_DIR: str = "/app/temp"
    MAX_UPLOAD_SIZE: int = 100
    
    MIN_MATCH_LENGTH: int = 10
    K_GRAM: int = 3
    WINDOW_SIZE: int = 4
    
    SBERT_MODEL: str = "firqaaa/indo-sentence-bert-base"

    SBERT_MODEL_PATH: str= "/model-cache/indo-sentence-bert-base"

    class Config:
        # Pydantic akan mencari file .env
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()