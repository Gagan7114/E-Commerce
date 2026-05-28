"""ModelView definitions for the sqladmin admin panel."""

from fastapi import Request
from sqladmin import ModelView
from sqladmin.fields import QuerySelectMultipleField
from wtforms import widgets as wtwidgets

from db.sqlalchemy_db import SessionLocal
from models.app_models import User, TruckDispatch, PlatformConfig
from models.permissions import Group, Permission
from models.warehouse import WAREHOUSE_MODELS
from routes.auth import _hash_password


# ─── Checkbox multi-select widget for M2M fields ─────────────────────
# Replaces the default scrollable <select multiple> (which requires Ctrl+Click
# to toggle) with a vertical list of checkboxes — one per option, add/remove
# independently.

class CheckboxMultiField(QuerySelectMultipleField):
    widget = wtwidgets.ListWidget(prefix_label=False)
    option_widget = wtwidgets.CheckboxInput()


# ─── helpers ─────────────────────────────────────────────────────────

def _user_has(request: Request, *codes: str) -> bool:
    """Check whether the user logged into /admin has every given permission code.

    Superusers always return True. Anonymous / non-superusers fall back to
    `user_perm_codes()` from permissions.py.
    """
    from permissions import user_perm_codes  # local import to avoid cycle

    user_id = request.session.get("admin_user_id") if hasattr(request, "session") else None
    if not user_id:
        return False
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user or not user.is_active:
            return False
        if user.is_superuser:
            return True
        held = user_perm_codes(user)
        return all(c in held for c in codes)


class PermissionAwareModelView(ModelView):
    """Base ModelView that gates access via permission codes.

    Subclass and set the permission codes. Empty string = always allow.
    """
    perm_access = "admin.access"   # needed to see the view at all
    perm_create = ""               # needed for +New button / POST
    perm_edit   = ""               # needed for edit form
    perm_delete = ""               # needed for delete action

    def is_accessible(self, request: Request) -> bool:
        return _user_has(request, self.perm_access) if self.perm_access else True

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)

    # sqladmin ≥0.20 exposes `has_create_permission` etc. per-request.
    def has_create_permission(self, request: Request) -> bool:
        return _user_has(request, self.perm_create) if self.perm_create else True

    def has_edit_permission(self, request: Request) -> bool:
        return _user_has(request, self.perm_edit) if self.perm_edit else True

    def has_delete_permission(self, request: Request) -> bool:
        return _user_has(request, self.perm_delete) if self.perm_delete else True


# ─── App-owned models (full CRUD) ────────────────────────────────────

class UserAdmin(PermissionAwareModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "Auth"

    perm_access = "admin.user.view"
    perm_create = "admin.user.add"
    perm_edit   = "admin.user.edit"
    perm_delete = "admin.user.delete"

    column_list = [
        User.id,
        User.email,
        User.is_superuser,
        User.is_active,
        User.groups,
        User.direct_permissions,
        User.created_at,
    ]
    column_labels = {
        User.groups: "Groups",
        User.direct_permissions: "Direct perms",
    }
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = ("id", True)

    form_columns = [
        User.email,
        User.password_hash,
        User.is_superuser,
        User.is_active,
        User.groups,
        User.direct_permissions,
    ]
    form_overrides = {
        "groups": CheckboxMultiField,
        "direct_permissions": CheckboxMultiField,
    }
    form_args = {
        "password_hash": {
            "label": "Password (plaintext on create / edit — will be hashed)"
        },
        "groups": {
            "label": "Groups",
            "description": "Assign one or more roles. Permissions are inherited from every selected group.",
        },
        "direct_permissions": {
            "label": "Direct permissions (override)",
            "description": "Grant individual permissions on top of group inheritance. Untick to revoke; this does not affect the user's groups.",
        },
    }

    async def on_model_change(self, data, model, is_created, request):
        """Hash the password before saving if it doesn't already look hashed.

        Our hash format is ``<salt>:<sha256hex>`` — two hex chunks separated
        by a colon. If the user typed a plain password in the form, rehash it.
        """
        pw = data.get("password_hash") or ""
        looks_hashed = ":" in pw and all(part and all(c in "0123456789abcdef" for c in part) for part in pw.split(":", 1))
        if pw and not looks_hashed:
            data["password_hash"] = _hash_password(pw)
        if data.get("email"):
            data["email"] = data["email"].strip().lower()


class GroupAdmin(PermissionAwareModelView, model=Group):
    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-users"
    category = "Auth"

    perm_access = "admin.group.manage"
    perm_create = "admin.group.manage"
    perm_edit   = "admin.group.manage"
    perm_delete = "admin.group.manage"

    column_list = [Group.id, Group.name, Group.description]
    column_searchable_list = [Group.name]
    form_columns = [Group.name, Group.description, Group.permissions]
    form_overrides = {"permissions": CheckboxMultiField}
    form_args = {
        "permissions": {
            "label": "Permissions",
            "description": "Tick to include a permission in this group; untick to remove it.",
        },
    }


class PermissionAdmin(PermissionAwareModelView, model=Permission):
    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-key"
    category = "Auth"

    perm_access = "admin.group.manage"
    # Permissions are seeded from code — block manual create/delete to keep
    # the DB list in sync with backend/permissions.py.
    can_create = False
    can_delete = False

    column_list = [Permission.id, Permission.code, Permission.description]
    column_searchable_list = [Permission.code, Permission.description]
    form_columns = [Permission.description]


class TruckDispatchAdmin(PermissionAwareModelView, model=TruckDispatch):
    name = "Truck Dispatch"
    name_plural = "Truck Dispatches"
    icon = "fa-solid fa-truck"
    category = "Operations"

    perm_access = "admin.dispatch.manage"
    perm_create = "admin.dispatch.manage"
    perm_edit   = "admin.dispatch.manage"
    perm_delete = "admin.dispatch.manage"

    column_list = [
        TruckDispatch.id,
        TruckDispatch.platform_slug,
        TruckDispatch.vehicle_number,
        TruckDispatch.driver_name,
        TruckDispatch.mode,
        TruckDispatch.truck_type,
        TruckDispatch.po_count,
        TruckDispatch.loaded_kg,
        TruckDispatch.fill_percentage,
        TruckDispatch.status,
        TruckDispatch.dispatch_date,
        TruckDispatch.created_at,
    ]
    column_searchable_list = [
        TruckDispatch.vehicle_number,
        TruckDispatch.driver_name,
        TruckDispatch.driver_phone,
        TruckDispatch.notes,
    ]
    column_sortable_list = [
        TruckDispatch.id,
        TruckDispatch.created_at,
        TruckDispatch.dispatch_date,
        TruckDispatch.platform_slug,
    ]
    column_default_sort = ("created_at", True)


class PlatformConfigAdmin(PermissionAwareModelView, model=PlatformConfig):
    name = "Platform"
    name_plural = "Platforms"
    icon = "fa-solid fa-plug"
    category = "Config"

    perm_access = "admin.platform.manage"
    perm_create = "admin.platform.manage"
    perm_edit   = "admin.platform.manage"
    perm_delete = "admin.platform.manage"

    column_list = [
        PlatformConfig.slug,
        PlatformConfig.name,
        PlatformConfig.inventory_table,
        PlatformConfig.secondary_table,
        PlatformConfig.master_po_table,
        PlatformConfig.po_filter_value,
        PlatformConfig.match_column,
        PlatformConfig.is_active,
    ]
    column_searchable_list = [PlatformConfig.slug, PlatformConfig.name]


APP_VIEWS = [UserAdmin, GroupAdmin, PermissionAdmin, TruckDispatchAdmin, PlatformConfigAdmin]


# ─── Warehouse models (read-only in admin) ───────────────────────────

def _build_readonly_view(model, table_name):
    """Generate a read-only, permission-gated ModelView for a warehouse table."""
    columns = list(model.__table__.columns)
    short_list = columns[:8]

    attrs = {
        "name": table_name,
        "name_plural": table_name,
        "icon": "fa-solid fa-database",
        "category": "Warehouse (read-only)",
        "perm_access": "admin.warehouse.view",
        "column_list": short_list,
        "column_sortable_list": [c for c in short_list if c.name in {"id", "created_at", "updated_at"}],
        "can_create": False,
        "can_edit": False,
        "can_delete": False,
        "can_export": True,
    }
    return type(
        f"{model.__name__}Admin",
        (PermissionAwareModelView,),
        attrs,
        model=model,
    )


WAREHOUSE_VIEWS = [_build_readonly_view(m, t) for t, m in WAREHOUSE_MODELS.items()]
