import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # API Settings (Gemini)
    # Support multiple keys separated by comma
    _keys_str = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    GEMINI_API_KEYS: list[str] = [k.strip() for k in _keys_str.split(",") if k.strip()]
    
    # Keep backward compatibility for single key usage
    GEMINI_API_KEY: str = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""

    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", os.getenv("OPENAI_MODEL", "gemini-2.0-flash"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME", "TestifyHub_bot")
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "https://s1qosimovv.github.io/testify-frontend/")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}

settings = Settings()
