"""StakeholderSim API - Main FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, health, conversations, grades, dashboard, assignments

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="StakeholderSim API",
    description="AI-powered role-play training platform for stakeholder communication",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(grades.router, prefix="/api/v1/grades", tags=["Grading"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(assignments.router, prefix="/api/v1/assignments", tags=["Assignments"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 50)
    print("StakeholderSim API Starting...")
    print(f"Environment: {settings.env}")
    print(f"Debug Mode: {settings.debug}")
    if settings.env == "development":
        print("")
        print("  WARNING: Using MOCK AUTHENTICATION")
        print("  See PRE_DEPLOYMENT_CHECKLIST.md before production")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("StakeholderSim API Shutting down...")
