# File: config.py
import os
from dotenv import load_dotenv

load_dotenv() 

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "rod-royale-db")
    
    # API Configuration
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")

    # CORS - Secure configuration
    cors_origins_str = os.getenv("CORS_ORIGINS", "*")
    BACKEND_CORS_ORIGINS: list = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sknmckbiyvajnjbosc")  # Use a secure key in production

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # Token Expiration Settings
    access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    if not access_token_expire_minutes.isdigit():
        access_token_expire_minutes = 30

    refresh_token_expire_days = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    if not refresh_token_expire_days.isdigit():
        refresh_token_expire_days = 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(refresh_token_expire_days)

    class Config:
        case_sensitive = True

settings = Settings()
