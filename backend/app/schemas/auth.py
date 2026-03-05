"""Pydantic schemas for authentication API."""

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    """Request to create a new account."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: str = Field("student", description="User role: student, instructor, or admin")


class LoginRequest(BaseModel):
    """Request to log in."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Current user response."""

    id: str
    email: str
    name: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
