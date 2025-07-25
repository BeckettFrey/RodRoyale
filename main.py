from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging


from config import settings
from database import connect_to_mongo, close_mongo_connection
from routers import users, catches, pins, uploads, auth, leaderboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Rod Royale Backend API...")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down Rod Royale Backend API...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="RESTful API for Rod Royale - A social fishing app",
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
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(catches.router, prefix=settings.API_V1_STR)
app.include_router(pins.router, prefix=settings.API_V1_STR)
app.include_router(uploads.router, prefix=settings.API_V1_STR)
app.include_router(leaderboard.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Rod Royale Backend API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Rod Royale-backend"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Check if SSL certificates exist for HTTPS
    ssl_keyfile = "certificates/private.key"
    ssl_certfile = "certificates/cert.pem"
    
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        print("🔐 Starting server with HTTPS (SSL certificates found)")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile
        )
    else:
        print("⚠️  Starting server with HTTP (no SSL certificates found)")
        print("   To enable HTTPS, run: ./generate_ssl_cert.sh")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
