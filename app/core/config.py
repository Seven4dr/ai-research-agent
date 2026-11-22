import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    # Répertoires
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RESEARCH_DIR: Path = BASE_DIR / "data" / "research"
    REPORTS_DIR: Path = BASE_DIR / "data" / "reports"
    
    # Clés API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "87866417202")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Paramètres d'exécution
    MAX_RESEARCH_CYCLES: int = int(os.getenv("MAX_RESEARCH_CYCLES", "2"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    DEFAULT_SEARCH_DEPTH: str = os.getenv("DEFAULT_SEARCH_DEPTH", "standard")
    
    # Limites selon le niveau de recherche
    DEPTH_CONFIG = {
        "rapide": {"max_queries": 2, "max_sources": 5, "tavily_depth": "basic"},
        "standard": {"max_queries": 4, "max_sources": 10, "tavily_depth": "basic"},
        "approfondie": {"max_queries": 6, "max_sources": 16, "tavily_depth": "advanced"}
    }

    @classmethod
    def ensure_directories(cls):
        """Assure que les répertoires nécessaires existent."""
        cls.RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
