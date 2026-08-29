import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    HF_TOKEN: str

    HF_API_URL: str = (
        "https://router.huggingface.co/hf-inference/models/"
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.3
    DEFAULT_TOP_K: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()