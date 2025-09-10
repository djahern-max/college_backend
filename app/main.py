# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import user, oauth, profiles, scholarships, institution, s2023_is
from fastapi.routing import APIRoute
from fastapi.responses import PlainTextResponse
from app.api.v1.admin import images as admin_images


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

# Include routers (only the ones that exist)
app.include_router(user.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["OAuth"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(
    institution.router, prefix="/api/v1/institutions", tags=["Institutions"]
)
app.include_router(
    scholarships.router, prefix="/api/v1/scholarships", tags=["Scholarships"]
)
app.include_router(
    admin_images.router, prefix="/api/v1/admin/images", tags=["admin-images"]
)
app.include_router(s2023_is.router, prefix="/api/v1", tags=["s2023-is"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CampusConnect API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CampusConnect API"}


@app.get("/routes-simple", response_class=PlainTextResponse)
async def get_routes_simple():
    """
    Returns a concise list of all routes with their paths and methods.
    """
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            routes.append(f"{methods}: {route.path}")

    return "\n".join(routes)
