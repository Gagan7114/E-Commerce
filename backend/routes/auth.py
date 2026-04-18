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

@router.post("/register")
async def register(body: AuthRequest):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute('SELECT id FROM users WHERE email = %s', (body.email,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            # Insert new user
            pw_hash = _hash_password(body.password)
            cur.execute(
                'INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id',
                (body.email, pw_hash),
            )
            user_id = cur.fetchone()[0]
            conn.commit()
        # Return token
        token = _create_jwt({
            "sub": user_id,
            "email": body.email,
            "exp": time.time() + JWT_EXPIRY_HOURS * 3600,
        })
        return {"user": {"id": user_id, "email": body.email}, "token": token}
    finally:
        put_conn(conn)


@router.post("/login")
async def login(body: AuthRequest):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, email, password_hash FROM users WHERE email = %s', (body.email,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            user_id, email, pw_hash = row
            if not _verify_password(body.password, pw_hash):
                raise HTTPException(status_code=401, detail="Invalid email or password")
        token = _create_jwt({
            "sub": user_id,
            "email": email,
            "exp": time.time() + JWT_EXPIRY_HOURS * 3600,
        })
        return {"user": {"id": user_id, "email": email}, "token": token}
    finally:
        put_conn(conn)


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user": user}
