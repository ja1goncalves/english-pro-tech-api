import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your_secret_key')
    ALGORITHM: str = os.getenv('ENCODE_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('TOKEN_TTL', 30)
    DB_URI: str = os.getenv('DB_URI', 'postgresql://username:password@localhost:5432/test')
    DB_NAME: str = os.getenv('DB_NAME', 'ept_db')
    ADMIN_PASSWORD: str = os.getenv('ADMIN_PASSWORD', 'admin123')
    FILE_UPLOAD_DIR: str = os.getenv('FILE_UPLOAD_DIR', './files')
    OPEN_ROUTES: list[str] = ["/api/v1/auth/token", "/api/v1/auth/reset-password", "/api/v1/user/register"]

    class Config:
        case_sensitive = True

settings = Settings()