from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import FRONTEND_URL, JWT_SECRET
from db.schema import ensure_schema
from routes import auth, dashboard, platform, sap, upload

ensure_schema()

app = FastAPI(title="E-Com Platform API", version="1.0.0")

# Session cookie for the /admin panel (sqladmin uses request.session).
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(platform.router)
app.include_router(sap.router)
app.include_router(upload.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Admin panel at /admin — mounted last so it sees all routes.
from admin.setup import mount_admin  # noqa: E402
mount_admin(app)
