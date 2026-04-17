from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL
from routes import auth, dashboard, platform, sap, upload

app = FastAPI(title="E-Com Platform API", version="1.0.0")

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(platform.router)
app.include_router(sap.router)
app.include_router(upload.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
