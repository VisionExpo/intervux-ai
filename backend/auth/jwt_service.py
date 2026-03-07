"""
JWT Authentication Service for Intervux AI.

This module provides JWT token-based authentication:
- Token creation
- Token verification
- User dependency injection
- Role-based access control
- Token rotation and revocation

Example usage:
    from backend.auth.jwt_service import get_current_user, create_access_token
    
    @app.get("/api/candidates")
    def get_candidates(user = Depends(get_current_user)):
        return {"user": user}
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict

# Configuration - should be set via environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "intervux-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "12"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# =========================================================
# Pydantic Models
# =========================================================


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    role: str = "viewer"
    exp: Optional[datetime] = None


class UserBase(BaseModel):
    """Base user model."""
    email: str
    role: str = "viewer"


class UserCreate(UserBase):
    """User creation model."""
    password: str
    name: str


class UserResponse(UserBase):
    """User response model."""
    id: str
    name: str
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """User login model."""
    email: str
    password: str


# =========================================================
# Token Functions
# =========================================================


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Payload data to encode
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_pair(user_data: Dict[str, Any]) -> Token:
    """
    Create both access and refresh tokens.
    
    Args:
        user_data: User data to encode in tokens
        
    Returns:
        Token object with both tokens
    """
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role", "viewer")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            email=email,
            role=role,
            exp=payload.get("exp"),
        )
        return token_data
        
    except JWTError:
        raise credentials_exception


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode token without verification (for debugging).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        return jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": False}
        )
    except Exception:
        return None


# =========================================================
# User Dependency
# =========================================================


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Get current authenticated user from JWT token.
    
    This is a FastAPI dependency that can be used to protect routes.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    return verify_token(token)


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Get current active user.
    
    This extends get_current_user to check if user is active.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        TokenData if user is active
        
    Raises:
        HTTPException: If user is inactive
    """
    # In a full implementation, this would check the database
    # For now, we assume all token-holders are active
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return current_user


# =========================================================
# Role-Based Access Control
# =========================================================


class Role:
    """Role constants."""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    VIEWER = "viewer"
    
    # Role hierarchy (higher index = more permissions)
    HIERARCHY = {
        ADMIN: 3,
        RECRUITER: 2,
        VIEWER: 1,
    }


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Example:
        @app.get("/api/admin/users")
        def admin_users(user = Depends(require_role("admin"))):
            return {"users": []}
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        FastAPI dependency that checks role
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        user_role = current_user.role
        user_level = Role.HIERARCHY.get(user_role, 0)
        required_level = Role.HIERARCHY.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' or higher required. Your role: '{user_role}'"
            )
        return current_user
    
    return role_checker


def require_any_role(roles: list[str]):
    """
    Dependency factory for multiple role access.
    
    Example:
        @app.get("/api/reports")
        def reports(user = Depends(require_any_role(["admin", "recruiter"]))):
            return {"reports": []}
    
    Args:
        roles: List of acceptable roles
        
    Returns:
        FastAPI dependency that checks any of the roles
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {roles} required. Your role: '{current_user.role}'"
            )
        return current_user
    
    return role_checker


# =========================================================
# Permission Checks
# =========================================================


class Permission:
    """Permission constants."""
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_MODELS = "manage_models"
    VIEW_EXPERIMENTS = "view_experiments"
    MANAGE_EXPERIMENTS = "manage_experiments"
    
    # Recruiter permissions
    VIEW_INTERVIEWS = "view_interviews"
    CONDUCT_INTERVIEW = "conduct_interview"
    VIEW_CANDIDATES = "view_candidates"
    MANAGE_CANDIDATES = "manage_candidates"
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    
    # Viewer permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_METRICS = "view_metrics"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.MANAGE_USERS,
        Permission.MANAGE_MODELS,
        Permission.VIEW_EXPERIMENTS,
        Permission.MANAGE_EXPERIMENTS,
        Permission.VIEW_INTERVIEWS,
        Permission.CONDUCT_INTERVIEW,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_CANDIDATES,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_METRICS,
    ],
    Role.RECRUITER: [
        Permission.VIEW_INTERVIEWS,
        Permission.CONDUCT_INTERVIEW,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_CANDIDATES,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_METRICS,
    ],
    Role.VIEWER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_METRICS,
    ],
}


def has_permission(role: str, permission: str) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: User role
        permission: Permission to check
        
    Returns:
        True if role has permission
    """
    return permission in ROLE_PERMISSIONS.get(role, [])


def require_permission(permission: str):
    """
    Dependency factory for permission-based access control.
    
    Example:
        @app.get("/api/admin/users")
        def users(user = Depends(require_permission("manage_users"))):
            return {"users": []}
    
    Args:
        permission: Permission required to access the endpoint
        
    Returns:
        FastAPI dependency that checks permission
    """
    async def permission_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required. Your role: '{current_user.role}'"
            )
        return current_user
    
    return permission_checker


# =========================================================
# Password Utilities
# =========================================================


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except Exception:
        # Fallback for development when passlib/bcrypt backend is unavailable.
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches
    """
    # SHA256 fallback hashes are 64-char hex strings.
    if len(hashed_password) == 64 and all(c in "0123456789abcdef" for c in hashed_password.lower()):
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


# =========================================================
# Token Refresh
# =========================================================


def refresh_access_token(refresh_token: str) -> Token:
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New token pair
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    token_data = verify_token(refresh_token)
    
    # Verify it's a refresh token
    payload = jwt.decode(
        refresh_token, 
        SECRET_KEY, 
        algorithms=[ALGORITHM],
        options={"verify_type": False}
    )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token."
        )
    
    # Create new token pair
    user_data = {
        "user_id": token_data.user_id,
        "email": token_data.email,
        "role": token_data.role,
    }
    
    return create_token_pair(user_data)


# =========================================================
# Demo Users (For Development)
# =========================================================


# In production, these would be stored in the database
DEMO_USERS = {
    "admin@intervux.ai": {
        "id": "admin-001",
        "email": "admin@intervux.ai",
        "name": "Admin User",
        "role": Role.ADMIN,
        "password_hash": hash_password("admin123"),
    },
    "recruiter@intervux.ai": {
        "id": "recruiter-001",
        "email": "recruiter@intervux.ai",
        "name": "Recruiter User",
        "role": Role.RECRUITER,
        "password_hash": hash_password("recruiter123"),
    },
    "viewer@intervux.ai": {
        "id": "viewer-001",
        "email": "viewer@intervux.ai",
        "name": "Viewer User",
        "role": Role.VIEWER,
        "password_hash": hash_password("viewer123"),
    },
}


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by email and password.
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        User data if authenticated, None otherwise
    """
    user = DEMO_USERS.get(email)
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return {
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email.
    
    Args:
        email: User email
        
    Returns:
        User data if found, None otherwise
    """
    user = DEMO_USERS.get(email)
    if not user:
        return None
    
    return {
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "password_hash": user.get("password_hash", ""),
    }


# =========================================================
# Token Revocation (Session Management)
# =========================================================

# In-memory storage for revoked tokens (use Redis in production)
_revoked_tokens: Set[str] = set()
_revoked_refresh_tokens: Set[str] = set()


def revoke_token(token: str) -> bool:
    """
    Revoke an access token (logout).
    
    Args:
        token: JWT token to revoke
        
    Returns:
        True if token was revoked
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": False}
        )
        jti = payload.get("jti") or payload.get("user_id")
        if jti:
            _revoked_tokens.add(jti)
            return True
    except Exception:
        pass
    return False


def revoke_refresh_token(token: str) -> bool:
    """
    Revoke a refresh token (logout/rotation).
    
    Args:
        token: Refresh token to revoke
        
    Returns:
        True if token was revoked
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": False}
        )
        jti = payload.get("jti") or payload.get("user_id")
        if jti:
            _revoked_refresh_tokens.add(jti)
            return True
    except Exception:
        pass
    return False


def is_token_revoked(token: str) -> bool:
    """
    Check if a token has been revoked.
    
    Args:
        token: JWT token to check
        
    Returns:
        True if token is revoked
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": False}
        )
        jti = payload.get("jti") or payload.get("user_id")
        return jti in _revoked_tokens
    except Exception:
        return False


def is_refresh_token_revoked(token: str) -> bool:
    """
    Check if a refresh token has been revoked.
    
    Args:
        token: Refresh token to check
        
    Returns:
        True if token is revoked
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": False}
        )
        jti = payload.get("jti") or payload.get("user_id")
        return jti in _revoked_refresh_tokens
    except Exception:
        return False


def create_token_pair_with_rotation(user_data: Dict[str, Any]) -> Token:
    """
    Create both access and refresh tokens with rotation.
    
    Each token gets a unique JWT ID (jti) for revocation tracking.
    
    Args:
        user_data: User data to encode in tokens
        
    Returns:
        Token object with both tokens
    """
    # Add unique JWT ID for each token
    access_data = user_data.copy()
    access_data["jti"] = str(uuid.uuid4())
    
    refresh_data = user_data.copy()
    refresh_data["jti"] = str(uuid.uuid4())
    
    access_token = create_access_token(access_data)
    refresh_token = create_refresh_token(refresh_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )


def refresh_access_token_with_rotation(refresh_token: str) -> Token:
    """
    Refresh an access token using a refresh token with rotation.
    
    Flow:
    - Validates the refresh token
    - Revokes the old refresh token
    - Issues new access and refresh tokens
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New token pair
        
    Raises:
        HTTPException: If refresh token is invalid or revoked
    """
    # Check if refresh token is revoked
    if is_refresh_token_revoked(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(refresh_token)
    
    # Verify it's a refresh token
    payload = jwt.decode(
        refresh_token, 
        SECRET_KEY, 
        algorithms=[ALGORITHM],
        options={"verify_type": False}
    )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token."
        )
    
    # Revoke the old refresh token (rotation)
    revoke_refresh_token(refresh_token)
    
    # Create new token pair with rotation
    user_data = {
        "user_id": token_data.user_id,
        "email": token_data.email,
        "role": token_data.role,
    }
    
    return create_token_pair_with_rotation(user_data)


# =========================================================
# API Key Authentication
# =========================================================

# In-memory API key storage (use database in production)
_api_keys: Dict[str, Dict[str, Any]] = {}


def create_api_key(name: str, user_id: str, role: str, expires_days: int = 365) -> str:
    """
    Create an API key for service-to-service authentication.
    
    Args:
        name: Name/description for the API key
        user_id: ID of the user owning this key
        role: Role to associate with this key
        expires_days: Days until key expires
        
    Returns:
        The API key string
    """
    import secrets
    api_key = f"ik_{secrets.token_urlsafe(32)}"
    
    _api_keys[api_key] = {
        "name": name,
        "user_id": user_id,
        "role": role,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=expires_days),
    }
    
    return api_key


def verify_api_key(api_key: str) -> Optional[TokenData]:
    """
    Verify an API key and return user data.
    
    Args:
        api_key: API key to verify
        
    Returns:
        TokenData if valid, None otherwise
    """
    key_data = _api_keys.get(api_key)
    
    if not key_data:
        return None
    
    # Check expiration
    if key_data["expires_at"] < datetime.utcnow():
        return None
    
    return TokenData(
        user_id=key_data["user_id"],
        email=f"api-{key_data['user_id']}@intervux.ai",
        role=key_data["role"],
    )


def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key.
    
    Args:
        api_key: API key to revoke
        
    Returns:
        True if key was revoked
    """
    if api_key in _api_keys:
        del _api_keys[api_key]
        return True
    return False


# Initialize demo API key for testing
_demo_api_key = create_api_key(
    name="Demo API Key",
    user_id="demo-api-user",
    role="recruiter",
    expires_days=365
)

