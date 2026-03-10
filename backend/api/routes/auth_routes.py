"""
Authentication Routes for Intervux AI.

This module provides authentication endpoints:
- Login
- Logout
- Token refresh
- User profile
- Change password

Example usage:
    from backend.api.routes.auth_routes import router
    
    app.include_router(router, prefix="/api/auth", tags=["auth"])
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth.jwt_service import (
    Token,
    TokenData,
    UserLogin,
    UserResponse,
    authenticate_user,
    create_token_pair,
    get_current_user,
    get_user_by_email,
    hash_password,
    refresh_access_token,
    verify_password,
    verify_token,
    Role,
)

router = APIRouter()


# =========================================================
# Login Endpoints
# =========================================================


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT tokens.
    
    Use OAuth2 form data with:
    - username: email address
    - password: password
    
    Returns access and refresh tokens.
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token = create_token_pair(user)
    
    return token


@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin):
    """
    Authenticate user using JSON payload.
    
    Alternative login endpoint that accepts JSON body.
    """
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token = create_token_pair(user)
    
    return token


# =========================================================
# Token Refresh
# =========================================================


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    
    Send the refresh_token received during login to get new tokens.
    """
    try:
        return refresh_access_token(refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =========================================================
# User Profile
# =========================================================


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns the profile of the currently authenticated user.
    """
    user = get_user_by_email(current_user.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["user_id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        is_active=True,
        created_at=datetime.utcnow(),
    )


# =========================================================
# Logout
# =========================================================


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout current user.
    
    In a full implementation, this would invalidate the token
    by adding it to a blacklist in Redis or database.
    """
    # In production, add token to blacklist
    # token_blacklist.add(current_user.exp)
    
    return {
        "message": "Successfully logged out",
        "user_id": current_user.user_id,
    }


# =========================================================
# Password Management
# =========================================================


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Change user password.
    
    Requires the current password to be verified before
    setting the new password.
    """
    user = get_user_by_email(current_user.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    # In production, this would check against database
    if not verify_password(old_password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # In production, update password in database
    # For demo, just return success
    return {
        "message": "Password changed successfully",
        "user_id": current_user.user_id,
    }


# =========================================================
# Role Management (Admin Only)
# =========================================================


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: TokenData = Depends(get_current_user)
):
    """
    List all users (admin only in production).
    
    For demo purposes, returns demo users.
    """
    # In production, query database
    from backend.auth.jwt_service import DEMO_USERS
    
    users = []
    for email, user_data in DEMO_USERS.items():
        users.append(UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            is_active=True,
            created_at=datetime.utcnow(),
        ))
    
    return users


# =========================================================
# Health Check
# =========================================================


@router.get("/health")
async def auth_health():
    """
    Check authentication service health.
    """
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.utcnow().isoformat(),
    }

