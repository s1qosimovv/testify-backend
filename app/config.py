import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # API Settings (Gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", os.getenv("OPENAI_MODEL", "gemini-2.0-flash"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}

settings = Settings()
