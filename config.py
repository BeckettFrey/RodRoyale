# File: config.py
import os

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "rod_royale_db")
    
    # API Configuration
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Rod Royale Backend API")

    # CORS - Secure configuration
    cors_origins_str = os.getenv("CORS_ORIGINS", "")
    BACKEND_CORS_ORIGINS: list = [origin for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    class Config:
        case_sensitive = True

settings = Settings()
