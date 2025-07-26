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
    
    # Get port from environment (for platforms like Heroku, Railway, etc.)
    port = int(os.environ.get("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        print("🚀 Starting production server...")
        print(f"   Environment: {environment}")
        print(f"   Port: {port}")
        print("   HTTPS handled by platform (Heroku, Railway, nginx, etc.)")
        # Production: Let platform handle HTTPS termination
        uvicorn.run("main:app", host="0.0.0.0", port=port)
    else:
        print("🛠️  Starting development server...")
        # Development: Check for SSL certificates
        ssl_keyfile = "certificates/private.key"
        ssl_certfile = "certificates/cert.pem"
        
        if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
            print("🔐 SSL certificates found - starting with HTTPS")
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=port, 
                reload=True,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile
            )
        else:
            print("⚠️  No SSL certificates found - starting with HTTP")
            print("   To enable HTTPS: ./generate_ssl_cert.sh")
            print("   For production: use platform SSL or reverse proxy")
            uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
