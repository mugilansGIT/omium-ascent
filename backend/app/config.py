from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AI Ops Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-min-32-chars!!"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    TAVILY_API_KEY: str = ""

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "ops@yourcompany.com"

    COMPANY_NAME: str = "Acme Corp"
    COMPANY_ADDRESS: str = "123 Business Park, Bengaluru 560001"
    COMPANY_PHONE: str = "+91-80-12345678"

    OMIUM_API_KEY: str = ""

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
