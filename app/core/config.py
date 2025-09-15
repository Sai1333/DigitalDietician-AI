import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env once
load_dotenv()

class Settings:
    ENV = os.getenv("ENV", "dev")

    # Comma-separated origins → list
    ALLOW_ORIGINS = [
        o.strip()
        for o in os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    # LLM provider (only Ollama now)
    LLM_PROVIDER = "ollama"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

@lru_cache
def get_settings() -> Settings:
    return Settings()
