import re
import sys
import os

filepath = "backend/auth/jwt_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# 1. verify_token
text = text.replace(
    """def verify_token(token: str) -> TokenData:""",
    """async def verify_token(token: str) -> TokenData:"""
)
verify_db_block = """        jti = payload.get("jti") or payload.get("user_id", "")
        if jti:
            db = SessionLocal()
            try:
                if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
                    raise credentials_exception
            finally:
                db.close()"""
new_verify_db_block = """        jti = payload.get("jti") or payload.get("user_id", "")
        if jti:
            from backend.db.database import AsyncSessionLocal, RevokedToken
            from sqlalchemy import select
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(RevokedToken).filter(RevokedToken.jti == jti))
                if result.scalar_one_or_none():
                    raise credentials_exception"""
text = text.replace(verify_db_block, new_verify_db_block)

# 2. get_current_user
text = text.replace(
    """    return verify_token(token)""",
    """    return await verify_token(token)"""
)

# 3. refresh_access_token
text = text.replace(
    """def refresh_access_token(refresh_token: str) -> Token:""",
    """async def refresh_access_token(refresh_token: str) -> Token:"""
)
text = text.replace(
    """    token_data = verify_token(refresh_token)""",
    """    token_data = await verify_token(refresh_token)"""
)

# 4. authenticate_user
text = text.replace(
    """def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:""",
    """async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:"""
)
auth_db_block = """        from backend.db.database import SessionLocal, User
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.email == email).first()
            if not db_user:
                return None
            if not verify_password(password, db_user.password_hash):
                return None
            return {
                "user_id": f"candidate-{db_user.id}",
                "email": db_user.email,
                "name": db_user.name,
                "role": db_user.role,
            }
        finally:
            db.close()"""
new_auth_db_block = """        from backend.db.database import AsyncSessionLocal, User
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).filter(User.email == email))
            db_user = result.scalar_one_or_none()
            if not db_user:
                return None
            if not verify_password(password, db_user.password_hash):
                return None
            return {
                "user_id": f"candidate-{db_user.id}",
                "email": db_user.email,
                "name": db_user.name,
                "role": db_user.role,
            }"""
text = text.replace(auth_db_block, new_auth_db_block)

# 5. get_user_by_email
text = text.replace(
    """def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:""",
    """async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:"""
)
email_db_block = """        from backend.db.database import SessionLocal, User
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.email == email).first()
            if not db_user:
                return None
            return {
                "user_id": f"candidate-{db_user.id}",
                "email": db_user.email,
                "name": db_user.name,
                "role": db_user.role,
                "password_hash": db_user.password_hash,
            }
        finally:
            db.close()"""
new_email_db_block = """        from backend.db.database import AsyncSessionLocal, User
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).filter(User.email == email))
            db_user = result.scalar_one_or_none()
            if not db_user:
                return None
            return {
                "user_id": f"candidate-{db_user.id}",
                "email": db_user.email,
                "name": db_user.name,
                "role": db_user.role,
                "password_hash": db_user.password_hash,
            }"""
text = text.replace(email_db_block, new_email_db_block)

# 6. refresh_access_token_with_rotation
text = text.replace(
    """def refresh_access_token_with_rotation(refresh_token: str) -> Token:""",
    """async def refresh_access_token_with_rotation(refresh_token: str) -> Token:"""
)
# Note: we already replaced "    token_data = verify_token(refresh_token)" with await in #3 but verify this block!
# Since there are multiple "    token_data = verify_token(refresh_token)", that replace string would have caught both.

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: jwt_service.py replaced")
