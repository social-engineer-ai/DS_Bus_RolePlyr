"""Authentication endpoints - MOCK AUTH FOR DEVELOPMENT ONLY.

WARNING: This is mock authentication for development purposes.
Before production deployment, replace with real OAuth 2.0.
See docs/PRE_DEPLOYMENT_CHECKLIST.md
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()
settings = get_settings()

# Mock user database (replace with real database in production)
MOCK_USERS = {
    "student1": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "student@example.com",
        "name": "Alex Student",
        "role": "student",
    },
    "student2": {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "student2@example.com",
        "name": "Jordan Student",
        "role": "student",
    },
    "instructor": {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "instructor@example.com",
        "name": "Dr. Taylor Instructor",
        "role": "instructor",
    },
    "admin": {
        "id": "44444444-4444-4444-4444-444444444444",
        "email": "admin@example.com",
        "name": "System Admin",
        "role": "admin",
    },
}


class MockLoginRequest(BaseModel):
    """Request to login as a mock user."""

    user_key: str  # One of: student1, student2, instructor, admin


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """Current user response."""

    id: str
    email: str
    name: str
    role: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def get_current_user_from_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        # Find user by ID
        for user in MOCK_USERS.values():
            if user["id"] == user_id:
                return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.get("/mock-users")
async def list_mock_users():
    """List available mock users for development.

    WARNING: This endpoint only exists in development mode.
    """
    if settings.env != "development":
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "warning": "MOCK AUTH - Development only. Replace before production.",
        "users": [
            {"key": key, "name": user["name"], "role": user["role"]}
            for key, user in MOCK_USERS.items()
        ],
    }


@router.post("/mock-login", response_model=TokenResponse)
async def mock_login(request: MockLoginRequest):
    """Login as a mock user for development.

    WARNING: This endpoint only exists in development mode.
    Replace with real OAuth 2.0 before production.
    """
    if settings.env != "development":
        raise HTTPException(status_code=404, detail="Not found")

    user = MOCK_USERS.get(request.user_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown user key. Available: {list(MOCK_USERS.keys())}",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(lambda: None)):
    """Get current authenticated user.

    Note: In a real app, this would use OAuth2PasswordBearer.
    For mock auth, pass token as query param: /me?token=xxx
    """
    # For now, return a placeholder - we'll implement proper token handling
    # when we add the auth middleware
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Use /mock-login first.",
    )
