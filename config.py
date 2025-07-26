import os

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "rod_royale_db")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Rod Royale Backend API"
    
    # CORS - Secure configuration
    # Set CORS_ORIGINS environment variable with comma-separated origins for production
    # Example: CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:8081,http://127.0.0.1:3000,http://127.0.0.1:8080,http://127.0.0.1:8081")
    BACKEND_CORS_ORIGINS: list = [origin.strip() for origin in os.getenv("CORS_ORIGINS", cors_origins_str).split(",") if origin.strip()]
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
