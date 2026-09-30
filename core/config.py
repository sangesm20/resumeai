from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    HF_TOKEN: str

    HF_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    DEFAULT_SIMILARITY_THRESHOLD: float = 0.0
    DEFAULT_TOP_K: int = 10

    # ==========================================
    # SCORING WEIGHTS FOR RESUME MATCHING
    # ==========================================
    SEMANTIC_WEIGHT: float = 0.60
    SKILL_WEIGHT: float = 0.25
    EXPERIENCE_WEIGHT: float = 0.15

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()