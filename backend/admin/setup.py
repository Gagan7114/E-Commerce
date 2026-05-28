"""Entrypoint that wires sqladmin into the FastAPI app."""

from pathlib import Path

from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from config import JWT_SECRET
from db.sqlalchemy_db import engine
from .auth import AdminAuth
from .views import APP_VIEWS, WAREHOUSE_VIEWS

_ADMIN_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _ADMIN_DIR / "templates"
_STATIC_DIR = _ADMIN_DIR / "static"


def mount_admin(app):
    # Serve our Django-admin-style CSS/JS at /admin-static (referenced by the
    # overridden base.html template). sqladmin's own /admin/statics mount only
    # exposes files inside the sqladmin package, so we need a separate mount.
    app.mount(
        "/admin-static",
        StaticFiles(directory=str(_STATIC_DIR)),
        name="admin-static",
    )

    admin = Admin(
        app,
        engine,
        base_url="/admin",
        title="E-Com Administration",
        authentication_backend=AdminAuth(secret_key=JWT_SECRET),
        templates_dir=str(_TEMPLATES_DIR),
    )

    for view in APP_VIEWS:
        admin.add_view(view)
    for view in WAREHOUSE_VIEWS:
        admin.add_view(view)

    return admin
