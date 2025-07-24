import os

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "catchy_db")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Catchy Backend API"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]  # Configure as needed for production
    
    class Config:
        case_sensitive = True

settings = Settings()
