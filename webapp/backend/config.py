from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "TraderMind"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Datenbank-Konfiguration
    # DATABASE_URL: str = "postgresql://postgres:IHR_PASSWORT_HIER@localhost:5432/tradermind"
    DATABASE_URL: str = "postgresql://postgres:(EEX$service)@localhost:5432/tradermind"
    
    # JWT-Konfiguration für zukünftige Authentifizierung
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 Tage
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()