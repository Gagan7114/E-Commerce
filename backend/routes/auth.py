"""
JWT-based auth endpoints. Stores users in the PostgreSQL 'users' table.
"""

import hashlib
import hmac
import os
import time
import json
import base64
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from db.postgres_client import get_conn, put_conn
from config import JWT_SECRET, JWT_EXPIRY_HOURS

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ─── JWT helpers (no external dependency) ───

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url_encode(json.dumps(header).encode())
    p = _b64url_encode(json.dumps(payload).encode())
    sig = hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"


def _decode_jwt(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    h, p, s = parts
    expected_sig = hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    actual_sig = _b64url_decode(s)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64url_decode(p))
    if payload.get("exp", 0) < time.time():
        raise ValueError("Token expired")
    return payload


# ─── Password hashing (SHA-256 + salt, no bcrypt dependency) ───

def _hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{h}"


def _verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":", 1)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == h


# ─── Ensure users table exists ───

def _ensure_users_table():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
    finally:
        put_conn(conn)


_ensure_users_table()


# ─── Dependency: get current user from token ───

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = _decode_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"id": payload["sub"], "email": payload["email"]}


# ─── Request models ───

class AuthRequest(BaseModel):
    email: str
    password: str


# ─── Endpoints ───

def _serialize_user(user_row):
    """Turn the ORM User into the JSON shape returned by /login /register /me."""
    from permissions import user_perm_codes  # local import to avoid cycle
    return {
        "id": user_row.id,
        "email": user_row.email,
        "is_superuser": bool(user_row.is_superuser),
        "is_active": bool(user_row.is_active),
        "groups": [g.name for g in user_row.groups],
        "permissions": sorted(user_perm_codes(user_row)),
    }


@router.post("/register")
async def register(body: AuthRequest):
    from db.sqlalchemy_db import SessionLocal
    from models.app_models import User as UserORM

    email = body.email.strip().lower()
    with SessionLocal() as session:
        if session.query(UserORM).filter(UserORM.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = UserORM(
            email=email,
            password_hash=_hash_password(body.password),
            is_superuser=False,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        token = _create_jwt({
            "sub": user.id,
            "email": user.email,
            "exp": time.time() + JWT_EXPIRY_HOURS * 3600,
        })
        return {"user": _serialize_user(user), "token": token}


@router.post("/login")
async def login(body: AuthRequest):
    from db.sqlalchemy_db import SessionLocal
    from models.app_models import User as UserORM

    email = body.email.strip().lower()
    with SessionLocal() as session:
        user = session.query(UserORM).filter(UserORM.email == email).first()
        if not user or not _verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")
        token = _create_jwt({
            "sub": user.id,
            "email": user.email,
            "exp": time.time() + JWT_EXPIRY_HOURS * 3600,
        })
        return {"user": _serialize_user(user), "token": token}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    from db.sqlalchemy_db import SessionLocal
    from models.app_models import User as UserORM

    with SessionLocal() as session:
        u = session.get(UserORM, user["id"])
        if not u or not u.is_active:
            raise HTTPException(status_code=401, detail="User not found or disabled")
        return {"user": _serialize_user(u)}
