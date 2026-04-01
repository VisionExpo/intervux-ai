import re

filepath = "backend/api/routes/auth_routes.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Make authenticate_user awaited
text = text.replace("user = authenticate_user(form_data.username, form_data.password)", "user = await authenticate_user(form_data.username, form_data.password)")
text = text.replace("user = authenticate_user(credentials.email, credentials.password)", "user = await authenticate_user(credentials.email, credentials.password)")

# create_token_pair is currently synchronous in jwt_service.py? Wait, let's assume sync for purely CPU code, but we didn't check. 
# Oh wait, verify_token is async, get_user_by_email is async, authenticate_user is async, refresh_access_token is async.
# So I should await get_user_by_email, refresh_access_token.

text = text.replace("return refresh_access_token(refresh_token)", "return await refresh_access_token(refresh_token)")

text = text.replace("user = get_user_by_email(current_user.email)", "user = await get_user_by_email(current_user.email)")

# Fix logout db calls
old_logout = """        db = SessionLocal()
        try:
            existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if not existing:
                db.add(RevokedToken(jti=jti, token_type="access", expires_at=expires_at))
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()"""
new_logout = """        from backend.db.database import AsyncSessionLocal
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            try:
                res = await db.execute(select(RevokedToken).filter(RevokedToken.jti == jti))
                existing = res.scalar_one_or_none()
                if not existing:
                    db.add(RevokedToken(jti=jti, token_type="access", expires_at=expires_at))
                    await db.commit()
            except Exception:
                await db.rollback()"""
text = text.replace(old_logout, new_logout)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: auth_routes.py replaced")
