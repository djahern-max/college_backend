"""
Main FastAPI application entry point - Updated with auth routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.config.settings import get_settings
from app.api.endpoints import health, users, auth, statistics, reviews, profiles
from app.db.database import engine, create_tables
from app.api.endpoints.scholarship import router as scholarship_router
import logging

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await create_tables()
    yield
    # Shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )

    # Add CORS middleware if not already configured
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Your Next.js frontend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount the uploads directory to serve static files
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(users.router, prefix="/api/v1", tags=["users"])
    app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
    app.include_router(scholarship_router, prefix="/api/v1", tags=["scholarships"])
    app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])
    app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])
    app.include_router(profiles.router, prefix="/api/v1", tags=["profiles"])
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )