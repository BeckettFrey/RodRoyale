from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import connect_to_mongo, close_mongo_connection
from routers import users, catches, pins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Catchy Backend API...")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down Catchy Backend API...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="RESTful API for Catchy - A social fishing app",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(catches.router, prefix=settings.API_V1_STR)
app.include_router(pins.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Catchy Backend API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "catchy-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
