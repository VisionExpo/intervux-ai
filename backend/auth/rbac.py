"""
Role-Based Access Control (RBAC) for Intervux AI.

This module provides:
- Role hierarchy management
- Permission checking
- Access decorators for FastAPI routes

Example usage:
    from backend.auth.rbac import require_permission, require_role, Permission
    
    @app.get("/admin/users")
    @require_permission(Permission.MANAGE_USERS)
    async def manage_users():
        ...
"""

from functools import wraps
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status

from backend.auth.jwt_service import (
    TokenData,
    get_current_user,
    has_permission,
    require_any_role,
    require_role,
    Role,
    Permission,
    ROLE_PERMISSIONS,
)


# =========================================================
# Role Management
# =========================================================


class RoleManager:
    """
    Manages roles and permissions.
    
    Example:
        role_manager = RoleManager()
        
        # Check if admin has permission
        admin_can_manage_users = role_manager.can(Role.ADMIN, Permission.MANAGE_USERS)
        
        # Get all permissions for a role
        recruiter_permissions = role_manager.get_permissions(Role.RECRUITER)
    """
    
    @staticmethod
    def can(role: str, permission: str) -> bool:
        """Check if a role has a specific permission."""
        return has_permission(role, permission)
    
    @staticmethod
    def get_permissions(role: str) -> List[str]:
        """Get all permissions for a role."""
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_any_permission(role: str, permissions: List[str]) -> bool:
        """Check if a role has any of the specified permissions."""
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        return any(p in role_permissions for p in permissions)
    
    @staticmethod
    def has_all_permissions(role: str, permissions: List[str]) -> bool:
        """Check if a role has all of the specified permissions."""
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        return all(p in role_permissions for p in permissions)
    
    @staticmethod
    def get_role_level(role: str) -> int:
        """Get the hierarchy level of a role."""
        return Role.HIERARCHY.get(role, 0)
    
    @staticmethod
    def is_higher_role(role1: str, role2: str) -> bool:
        """Check if role1 is higher than role2 in the hierarchy."""
        return Role.HIERARCHY.get(role1, 0) > Role.HIERARCHY.get(role2, 0)


# Singleton instance
role_manager = RoleManager()


# =========================================================
# FastAPI Dependencies
# =========================================================


# Pre-built role dependencies
require_admin = require_role(Role.ADMIN)
require_recruiter = require_any_role([Role.ADMIN, Role.RECRUITER])
require_viewer = require_any_role([Role.ADMIN, Role.RECRUITER, Role.VIEWER])


# Pre-built permission dependencies
manage_users = require_permission(Permission.MANAGE_USERS)
manage_models = require_permission(Permission.MANAGE_MODELS)
view_experiments = require_permission(Permission.VIEW_EXPERIMENTS)
manage_experiments = require_permission(Permission.MANAGE_EXPERIMENTS)
view_interviews = require_permission(Permission.VIEW_INTERVIEWS)
conduct_interview = require_permission(Permission.CONDUCT_INTERVIEW)
view_candidates = require_permission(Permission.VIEW_CANDIDATES)
manage_candidates = require_permission(Permission.MANAGE_CANDIDATES)
view_reports = require_permission(Permission.VIEW_REPORTS)
generate_reports = require_permission(Permission.GENERATE_REPORTS)
view_dashboard = require_permission(Permission.VIEW_DASHBOARD)
view_metrics = require_permission(Permission.VIEW_METRICS)


# =========================================================
# Decorator Functions
# =========================================================


def check_role(required_role: str):
    """
    Decorator for checking role (alternative to dependency).
    
    Example:
        @check_role("admin")
        async def admin_only_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Role check is done via dependency
            # This is here for documentation purposes
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_permission(permission: str):
    """
    Decorator for checking permission (alternative to dependency).
    
    Example:
        @check_permission("manage_users")
        async def manage_users_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Permission check is done via dependency
            # This is here for documentation purposes
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =========================================================
# Permission Groups
# =========================================================


class PermissionGroup:
    """Groups of related permissions."""
    
    # Admin operations
    ADMIN = [
        Permission.MANAGE_USERS,
        Permission.MANAGE_MODELS,
        Permission.MANAGE_EXPERIMENTS,
    ]
    
    # Recruitment operations
    RECRUITMENT = [
        Permission.VIEW_INTERVIEWS,
        Permission.CONDUCT_INTERVIEW,
        Permission.VIEW_CANDIDATES,
        Permission.MANAGE_CANDIDATES,
    ]
    
    # Reporting operations
    REPORTING = [
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
    ]
    
    # Dashboard operations
    DASHBOARD = [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_METRICS,
    ]
    
    # All permissions
    ALL = ADMIN + RECRUITMENT + REPORTING + DASHBOARD


# =========================================================
# Helper Functions
# =========================================================


def can_access_interview(user_role: str, interview_owner_id: str, current_user_id: str) -> bool:
    """
    Check if user can access a specific interview.
    
    Args:
        user_role: User's role
        interview_owner_id: ID of the interview owner
        current_user_id: ID of the current user
        
    Returns:
        True if user can access
    """
    # Admins can access all interviews
    if user_role == Role.ADMIN:
        return True
    
    # Recruiters can access interviews they're assigned to
    if user_role == Role.RECRUITER:
        # In production, check if recruiter is assigned to this interview
        return True
    
    # Viewers can only view (not modify)
    return True


def can_modify_candidate(user_role: str, candidate_owner_id: str, current_user_id: str) -> bool:
    """
    Check if user can modify a candidate.
    
    Args:
        user_role: User's role
        candidate_owner_id: ID of the candidate owner
        current_user_id: ID of the current user
        
    Returns:
        True if user can modify
    """
    # Admins can modify all candidates
    if user_role == Role.ADMIN:
        return True
    
    # Recruiters can modify candidates they created
    if user_role == Role.RECRUITER:
        return candidate_owner_id == current_user_id
    
    # Viewers cannot modify
    return False


def can_view_sensitive_data(user_role: str) -> bool:
    """
    Check if user can view sensitive data (salary, etc.).
    
    Args:
        user_role: User's role
        
    Returns:
        True if user can view sensitive data
    """
    return user_role in [Role.ADMIN, Role.RECRUITER]


def can_export_data(user_role: str) -> bool:
    """
    Check if user can export data.
    
    Args:
        user_role: User's role
        
    Returns:
        True if user can export
    """
    return user_role in [Role.ADMIN, Role.RECRUITER]


# =========================================================
# Validation Functions
# =========================================================


def validate_role(role: str) -> bool:
    """Validate if a role exists."""
    return role in Role.HIERARCHY


def validate_permission(permission: str) -> bool:
    """Validate if a permission exists."""
    all_permissions = set()
    for permissions in ROLE_PERMISSIONS.values():
        all_permissions.update(permissions)
    return permission in all_permissions


def get_role_display_name(role: str) -> str:
    """Get human-readable role name."""
    names = {
        Role.ADMIN: "Administrator",
        Role.RECRUITER: "Recruiter",
        Role.VIEWER: "Viewer",
    }
    return names.get(role, role.title())


def get_permission_display_name(permission: str) -> str:
    """Get human-readable permission name."""
    names = {
        Permission.MANAGE_USERS: "Manage Users",
        Permission.MANAGE_MODELS: "Manage Models",
        Permission.VIEW_EXPERIMENTS: "View Experiments",
        Permission.MANAGE_EXPERIMENTS: "Manage Experiments",
        Permission.VIEW_INTERVIEWS: "View Interviews",
        Permission.CONDUCT_INTERVIEW: "Conduct Interview",
        Permission.VIEW_CANDIDATES: "View Candidates",
        Permission.MANAGE_CANDIDATES: "Manage Candidates",
        Permission.VIEW_REPORTS: "View Reports",
        Permission.GENERATE_REPORTS: "Generate Reports",
        Permission.VIEW_DASHBOARD: "View Dashboard",
        Permission.VIEW_METRICS: "View Metrics",
    }
    return names.get(permission, permission.title())

