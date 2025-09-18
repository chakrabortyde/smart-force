import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "models/gemini-1.5-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    CHROMA_DIR: str = "./chromadb"
    DATA_DIR: str = "./data"
    REDIS_URL: str = "redis://localhost:6379/0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    HUGGINGFACEHUB_API_TOKEN: str =""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
