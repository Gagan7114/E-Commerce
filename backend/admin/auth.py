"""
AuthenticationBackend for sqladmin. Uses the existing `users` table and the
same SHA256+salt hash format as routes/auth.py. Only `is_superuser=True`
accounts may log in to /admin.
"""

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from db.sqlalchemy_db import SessionLocal
from models.app_models import User
from routes.auth import _verify_password


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = (form.get("username") or "").strip().lower()
        password = form.get("password") or ""
        if not email or not password:
            return False

        with SessionLocal() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user or not user.is_active or not user.is_superuser:
                return False
            if not _verify_password(password, user.password_hash):
                return False

        request.session.update({"admin_user_id": user.id, "admin_email": user.email})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        with SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active or not user.is_superuser:
                return False
        return True
