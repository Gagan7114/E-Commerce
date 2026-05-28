# Permissions & Roles

Django-style RBAC baked into the FastAPI backend. Central catalog lives in
[permissions.py](permissions.py); database tables are seeded from it.

**Rules of the road:**

- **Superusers bypass every check.** `users.is_superuser = TRUE` → every permission code is implicitly held.
- **Non-superusers accumulate permissions** from all Groups they belong to + any direct user permissions.
- **Permission codes follow `<resource>.<action>`** — e.g. `dashboard.view`, `dispatch.add`.
- **Re-seeding is idempotent.** Running `seed_permissions` never drops user→group links; it only syncs the *definitions*.

---

## 1. Permission catalog (25 codes)

| Code | Grants |
|---|---|
| **Dashboard** | |
| `dashboard.view` | Open the main dashboard home |
| `dashboard.table.view` | Browse any warehouse table via the dashboard's table browser |
| `dashboard.inspect` | Hit the `/api/dashboard/inspect/{table}` diagnostic endpoint |
| **Per-platform (read)** | |
| `platform.view` | Enter any `/platform/{slug}` page at all |
| `platform.stats.view` | See the 4-card stats block |
| `platform.po.view` | Open PO & Stock pages |
| `platform.inventory.view` | Open platform Inventory pages |
| `platform.secondary.view` | Open Secondary Sales pages |
| **Dispatch / Truck loading** | |
| `dispatch.view` | See the Dispatches list |
| `dispatch.add` | Create a new dispatch (Truck Loading flow) |
| `dispatch.edit` | Modify an existing dispatch |
| `dispatch.delete` | Remove a dispatch |
| **Distributors + SAP** | |
| `distributor.view` | Distributors page |
| `sap.view` | Generic `/api/sap/*` reads |
| `sap.invoice.view` | SAP sales invoices specifically |
| **Upload** | |
| `upload.use` | POST rows via `/api/upload/batch` |
| **Admin panel** | |
| `admin.access` | Minimum — required to reach `/admin` at all |
| `admin.user.view` / `.add` / `.edit` / `.delete` | CRUD on the User admin view |
| `admin.group.manage` | CRUD on Groups; view Permission list |
| `admin.dispatch.manage` | Full CRUD on TruckDispatch in admin |
| `admin.platform.manage` | Edit PlatformConfig rows |
| `admin.warehouse.view` | Browse the 18 warehouse tables in admin |

---

## 2. Default groups (roles)

Run [scripts/seed_permissions.py](scripts/seed_permissions.py) to insert/update these groups in the DB.

| Group | # perms | Intended for |
|---|---:|---|
| **Super Admin** | 25 | Break-glass fallback — same as `is_superuser=True`. Use the flag by default. |
| **Platform Admin** | 19 | Senior operations — full access to all platform ops, dispatches, and the platform config. **Cannot** touch users or groups. |
| **Operations Manager** | 14 | Runs dispatches end-to-end. Full read on platform data + full dispatch CRUD. Can manage dispatches in admin + browse warehouse. |
| **Dispatch Operator** | 7 | Frontline warehouse — only creates dispatches; no admin access. |
| **Finance Analyst** | 8 | Reads SAP invoices, distributors, and dashboard summaries for reconciliation. |
| **Viewer** | 13 | Read-only across *every* `.view` permission. Safe demo/audit role. |
| **Uploader** | 1 | Service account for the external uploader — only `upload.use`. |

### Full breakdown per role

<details><summary><strong>Platform Admin</strong> (19)</summary>

```
dashboard.view         dashboard.table.view   dashboard.inspect
platform.view          platform.stats.view    platform.po.view
platform.inventory.view  platform.secondary.view
dispatch.view  dispatch.add  dispatch.edit  dispatch.delete
distributor.view
sap.view  sap.invoice.view
admin.access  admin.dispatch.manage  admin.platform.manage
admin.warehouse.view
```
</details>

<details><summary><strong>Operations Manager</strong> (14)</summary>

```
dashboard.view  dashboard.table.view
platform.view  platform.stats.view  platform.po.view
platform.inventory.view  platform.secondary.view
dispatch.view  dispatch.add  dispatch.edit
distributor.view
admin.access  admin.dispatch.manage  admin.warehouse.view
```
</details>

<details><summary><strong>Dispatch Operator</strong> (7)</summary>

```
dashboard.view
platform.view  platform.stats.view  platform.po.view
platform.inventory.view
dispatch.view  dispatch.add
```
</details>

<details><summary><strong>Finance Analyst</strong> (8)</summary>

```
dashboard.view
platform.view  platform.stats.view
distributor.view
sap.view  sap.invoice.view
admin.access  admin.warehouse.view
```
</details>

<details><summary><strong>Viewer</strong> (13)</summary>

All `*.view` permissions (`dashboard.view`, `dashboard.table.view`, `platform.view`, `platform.stats.view`, `platform.po.view`, `platform.inventory.view`, `platform.secondary.view`, `dispatch.view`, `distributor.view`, `sap.view`, `sap.invoice.view`, `admin.user.view`, `admin.warehouse.view`).
</details>

---

## 3. First-time setup

```bash
cd backend
venv\Scripts\activate
python manage.py  # placeholder — we don't have this; use lines below instead
```

Real commands:

```bash
python -m scripts.seed_permissions            # seed catalog + default groups
python -m scripts.create_superuser --email admin@jivo.in --password ...
python -m scripts.assign_user_to_group --list # show every user's groups
```

---

## 4. Assigning users to roles

```bash
# single role
python -m scripts.assign_user_to_group --email ops@jivo.in --group "Operations Manager"

# multiple roles (additive)
python -m scripts.assign_user_to_group --email hybrid@jivo.in \
       --group "Viewer" --group "Uploader"

# remove all groups
python -m scripts.assign_user_to_group --email ops@jivo.in --clear
```

Or via the admin UI:

1. Log into `/admin` as a superuser.
2. **Users → click user → Groups field → select → Save.**
3. To create a brand-new role: **Groups → +New Group → name + description → check the permissions → Save.**
4. To see what a permission code means: **Permissions → (code column)** — descriptions are synced from [permissions.py](permissions.py).

---

## 5. How to enforce a permission on a route

The infrastructure is in place but **not yet applied to the existing API routes** (they're still `AllowAny` so the frontend keeps working). To lock a route down:

```python
from fastapi import Depends
from permissions import require_perm

@router.delete(
    "/{slug}/dispatches/{dispatch_id}",
    dependencies=[Depends(require_perm("dispatch.delete"))],
)
async def delete_dispatch(...):
    ...
```

or to get the user object:

```python
@router.post("/{slug}/dispatches")
async def create_dispatch(..., user = Depends(require_perm("dispatch.add"))):
    ...  # `user` is the ORM User; user.id / user.email available
```

Request without JWT → `401`. JWT valid but missing the permission → `403 Missing permission(s): dispatch.add`.

### Frontend can tailor UI using `/me`

The existing `GET /api/auth/me` now returns `groups` + `permissions`:

```json
{
  "user": {
    "id": 6,
    "email": "ops@jivo.in",
    "is_superuser": false,
    "is_active": true,
    "groups": ["Operations Manager"],
    "permissions": ["admin.access", "dashboard.view", ...]
  }
}
```

Use that to hide buttons a user can't act on (e.g., hide the "Delete" button when `"dispatch.delete"` isn't in the list). Backend enforcement still needs `require_perm` on the route.

---

## 6. Admin-panel enforcement (automatic)

The admin views already check permissions via `PermissionAwareModelView`:

| Action | Required permission |
|---|---|
| See the view in sidebar | `perm_access` (e.g. `admin.user.view`) |
| Click **+ New** | `perm_create` (e.g. `admin.user.add`) |
| Edit an existing row | `perm_edit`   (e.g. `admin.user.edit`) |
| Delete a row | `perm_delete` (e.g. `admin.user.delete`) |

Users who don't hold `perm_access` for a view simply don't see it in the sidebar. If they type the URL directly, sqladmin returns a 403.

---

## 7. Architecture

```
users ─┬── user_groups ──┬── groups ── group_permissions ── permissions
       │                                                        ▲
       └── user_permissions ────────────────────────────────────┘
                   (direct user overrides; optional)
```

Effective permission set:
```
codes(user) = user.direct_permissions  ∪  ⋃  group.permissions  for group in user.groups
```

Superuser short-circuit: if `is_superuser` is true, `codes(user) = ALL_CODES` regardless of any row in user_groups or user_permissions.

**Files:**
- [db/schema.py](db/schema.py) — DDL for `permissions`, `groups`, `group_permissions`, `user_groups`, `user_permissions`
- [models/permissions.py](models/permissions.py) — SQLAlchemy models + association tables
- [models/app_models.py](models/app_models.py) — `User.groups`, `User.direct_permissions`, `User.all_permission_codes()`
- [permissions.py](permissions.py) — source-of-truth registry, role catalog, `has_perm()`, `require_perm()`
- [scripts/seed_permissions.py](scripts/seed_permissions.py) — idempotent catalog → DB sync
- [scripts/assign_user_to_group.py](scripts/assign_user_to_group.py) — CLI for user↔group
- [admin/views.py](admin/views.py) — `PermissionAwareModelView` + GroupAdmin + PermissionAdmin

---

## 8. Adding a new permission

1. Add a new `(code, description)` tuple to the `PERMISSIONS` list in [permissions.py](permissions.py).
2. (Optional) add it to one or more roles in `ROLES`.
3. Re-run `python -m scripts.seed_permissions`. New perm appears in DB; groups get the new code.
4. Apply it to a route: `Depends(require_perm("your.new.code"))`.

No DB migration needed — the `permissions` table is flat.

---

## 9. Adding a new role

1. Add a key to `ROLES` in [permissions.py](permissions.py) with `description` + `perms` glob list.
2. Re-seed.
3. Assign users via the admin UI or CLI.

---

## 10. Troubleshooting

### `/admin/login` accepts my password but the dashboard shows blank sidebar
The user logged in but holds no permissions. Either promote to superuser or
add them to a group that includes `admin.access` + relevant model perms.

### `/api/auth/me` returns empty `permissions` list
- User not assigned to any group yet? `python -m scripts.assign_user_to_group --list`
- Superuser? `SELECT is_superuser FROM users WHERE email=…` — superusers return every code regardless of groups.

### Want to test as a specific role without changing a real user's groups
Create a dummy user: `python -m scripts.create_superuser --email role-test@x --password test` (this creates a superuser — remove the superuser flag in admin afterwards), then assign them to the group you're testing.
