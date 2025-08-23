from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users

# Import profiles and oauth when they're available:
# from app.api.v1 import profiles, oauth

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CampusConnect - Scholarship matching platform",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use dynamic configuration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# Include these when available:
# app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
# app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["OAuth"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CampusConnect API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CampusConnect API"}
