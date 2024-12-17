# app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Genesis API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Debug mode
    DEBUG: bool = False
    
    # API Keys
    ANTHROPIC_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "../../unwinded-408807-4d9a2e780f28.json"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allows extra fields in the environment without raising errors

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()