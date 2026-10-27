from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

    openai_api_key: str
    llm_model : str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    docs_dir: str = "data/docs"
    qdrant_path : str = ".qdrant"
    collection: str = "docs"
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 4
    judge_model: str= "gpt-4o-mini"

@lru_cache
def get_settings() -> Settings:
    return Settings()