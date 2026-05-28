"""
Permission registry + default role catalog + helpers.

Central source of truth for:
1. What permission codes exist (`PERMISSIONS` — (code, description) pairs).
2. What each default role grants (`ROLES` — group name → list of codes/globs).
3. Helpers used by routes and admin views (`has_perm`, `require_perm`, `user_perm_codes`).

Code format:   <resource>.<action>          e.g. "dashboard.view", "dispatch.add"
Wildcards supported in roles:
    "*"            — every permission
    "dispatch.*"   — every dispatch.* permission
    "*.view"       — every *.view permission
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.sqlalchemy_db import SessionLocal
from models.app_models import User
from routes.auth import _decode_jwt


# ─── 1. Permission catalog ────────────────────────────────────────────
# Grouped loosely by module for readability in /admin and docs.

PERMISSIONS = [
    # Dashboard (home overview, table browser, charts, alerts)
    ("dashboard.view",               "View main dashboard"),
    ("dashboard.table.view",         "Browse any warehouse table in the dashboard"),
    ("dashboard.inspect",            "Use the table inspect endpoint"),

    # Per-platform read access (stats cards, PO list, inventory match)
    ("platform.view",                "Enter any platform's section"),
    ("platform.stats.view",          "View platform stats cards"),
    ("platform.po.view",             "View POs"),
    ("platform.inventory.view",      "View platform inventory"),
    ("platform.secondary.view",      "View secondary-sales data"),

    # Dispatch / Truck Loading lifecycle
    ("dispatch.view",                "View dispatches"),
    ("dispatch.add",                 "Create (dispatch a truck)"),
    ("dispatch.edit",                "Edit dispatches"),
    ("dispatch.delete",              "Delete dispatches"),

    # Distributors + SAP
    ("distributor.view",             "View distributors page"),
    ("sap.view",                     "Query SAP endpoints"),
    ("sap.invoice.view",             "View SAP sales invoices"),

    # Uploader (external tool POSTs here)
    ("upload.use",                   "Bulk insert/upsert via /api/upload/batch"),

    # Admin panel access + model-level admin
    ("admin.access",                 "Access the /admin panel at all"),
    ("admin.user.view",              "View users in admin"),
    ("admin.user.add",               "Create users in admin"),
    ("admin.user.edit",              "Edit users in admin"),
    ("admin.user.delete",            "Delete users in admin"),
    ("admin.group.manage",           "Manage groups & permissions in admin"),
    ("admin.dispatch.manage",        "Manage TruckDispatch rows in admin (CRUD)"),
    ("admin.platform.manage",        "Edit the Platform config rows"),
    ("admin.warehouse.view",         "Browse warehouse tables in admin (read-only)"),
]

ALL_CODES = {code for code, _ in PERMISSIONS}


# ─── 2. Default role catalog ──────────────────────────────────────────
# Each role is a named Group with a list of permission patterns.

ROLES = {
    "Super Admin": {
        "description": "Full access. (Normally use is_superuser flag instead — this role exists as a backup.)",
        "perms": ["*"],
    },

    "Platform Admin": {
        "description": "Full operational access across all platforms. Can manage dispatches and edit platform config. Cannot manage users/groups.",
        "perms": [
            "dashboard.*",
            "platform.*",
            "dispatch.*",
            "distributor.view", "sap.*",
            "admin.access", "admin.dispatch.manage", "admin.platform.manage",
            "admin.warehouse.view",
        ],
    },

    "Operations Manager": {
        "description": "Creates and manages dispatches, reads all operational data. No platform config edits.",
        "perms": [
            "dashboard.view", "dashboard.table.view",
            "platform.view", "platform.stats.view", "platform.po.view",
            "platform.inventory.view", "platform.secondary.view",
            "dispatch.view", "dispatch.add", "dispatch.edit",
            "distributor.view",
            "admin.access", "admin.dispatch.manage", "admin.warehouse.view",
        ],
    },

    "Dispatch Operator": {
        "description": "Frontline truck-loading operator. Sees POs, creates dispatches. No admin access.",
        "perms": [
            "dashboard.view",
            "platform.view", "platform.stats.view", "platform.po.view",
            "platform.inventory.view",
            "dispatch.view", "dispatch.add",
        ],
    },

    "Finance Analyst": {
        "description": "Read-only access to SAP invoices and distributor data for reconciliation.",
        "perms": [
            "dashboard.view",
            "platform.view", "platform.stats.view",
            "distributor.view",
            "sap.*",
            "admin.access", "admin.warehouse.view",
        ],
    },

    "Viewer": {
        "description": "Read-only across operational data. Cannot create/edit anything.",
        "perms": [
            "*.view",
        ],
    },

    "Uploader": {
        "description": "External integration account — only allowed to POST /api/upload/batch.",
        "perms": ["upload.use"],
    },
}


# ─── 3. Glob → concrete code expansion ────────────────────────────────

def _expand_patterns(patterns):
    out = set()
    for p in patterns:
        if p == "*":
            out.update(ALL_CODES)
        elif p.endswith(".*"):
            prefix = p[:-1]  # keep trailing "."
            out.update(c for c in ALL_CODES if c.startswith(prefix))
        elif p.startswith("*."):
            suffix = p[1:]   # keep leading "."
            out.update(c for c in ALL_CODES if c.endswith(suffix))
        else:
            if p in ALL_CODES:
                out.add(p)
    return out


# ─── 4. Runtime helpers ───────────────────────────────────────────────

def user_perm_codes(user: User) -> set:
    """Return the set of permission codes this user effectively holds."""
    if not user or not user.is_active:
        return set()
    if user.is_superuser:
        return set(ALL_CODES)
    return user.all_permission_codes()


def has_perm(user: User, code: str) -> bool:
    """Check a single permission code against the user's effective set."""
    return code in user_perm_codes(user)


# ─── 5. FastAPI dependency ────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=True)


def _get_user_from_jwt(creds: HTTPAuthorizationCredentials) -> User:
    try:
        payload = _decode_jwt(creds.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")
        # Trigger eager-loaded groups/perms while session is open
        _ = user_perm_codes(user)
        session.expunge(user)
        return user


def require_perm(*codes: str):
    """FastAPI dependency factory. Usage:

        @router.get("/secret", dependencies=[Depends(require_perm("dashboard.view"))])
        def secret(): ...
    """
    def dep(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> User:
        user = _get_user_from_jwt(creds)
        codes_held = user_perm_codes(user)
        if not all(c in codes_held for c in codes):
            missing = [c for c in codes if c not in codes_held]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission(s): {', '.join(missing)}",
            )
        return user

    return dep


def current_user_optional():
    """Dependency that returns the User if authed, None otherwise (for /me-like endpoints)."""
    bearer = HTTPBearer(auto_error=False)

    def dep(creds: HTTPAuthorizationCredentials = Depends(bearer)):
        if not creds:
            return None
        try:
            return _get_user_from_jwt(creds)
        except HTTPException:
            return None

    return dep
