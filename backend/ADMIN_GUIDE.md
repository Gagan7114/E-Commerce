# Admin Panel (Django-style, FastAPI + sqladmin)

Mounted at **`http://localhost:8000/admin`**. Looks and behaves like Django's
admin — login page, model list pages, add / edit / delete forms, and a
sidebar grouping every registered table.

---

## 1. First-time setup

New deps added: `sqladmin`, `sqlalchemy`, `itsdangerous`, `jinja2`, `python-multipart`. Install:

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

On the next `uvicorn main:app` run, `ensure_schema()` will:
- Add `is_superuser` and `is_active` columns to the existing `users` table
  (idempotent — safe to re-run).
- Create `truck_dispatches` if missing (already there for most installs).
- Create `platform_config` + seed it with the 7 platforms (blinkit, zepto,
  jiomart, amazon, bigbasket, swiggy, flipkart). `ON CONFLICT DO NOTHING`
  — won't overwrite your edits.

---

## 2. Create your first superuser

```bash
# interactive (prompts for password)
python -m scripts.create_superuser

# non-interactive
python -m scripts.create_superuser --email admin@jivo.in --password SuperSecret123
```

Re-running promotes an existing user to superuser and resets their password.

---

## 3. Logging in

Start the server:

```bash
uvicorn main:app --reload
```

Open **`http://localhost:8000/admin`** → you'll see the sqladmin login page.
Use the email + password from step 2.

Only users with `is_superuser=True AND is_active=True` can log in. All others
are rejected at the form with "Invalid credentials".

---

## 4. What you can manage

The sidebar groups views into three categories:

### Auth
- **Users** — list/add/edit/delete. When you type a plain-text password in the
  form, it's auto-hashed (same salt+SHA256 format as the JWT auth endpoints).
  Already-hashed values (detected by the `salt:hexdigest` pattern) are left
  alone.

### Operations
- **Truck Dispatches** — every row inserted by the Truck Loading page. Full CRUD.

### Config
- **Platforms** — the 7-platform config that used to be hardcoded in
  [routes/platform.py](routes/platform.py). You can now toggle `is_active`,
  rename a platform, or point it at a different inventory table. Changes
  take effect within **30 seconds** (there's an in-process cache — no
  restart needed).

### Warehouse (read-only)
- **master_po, test_master_po** — PO tables
- **blinkit_inventory, zepto_inventory, …** — all 6 platform inventory tables
- **all_platform_inventory**
- **blinkitSec, zeptoSec, swiggySec, …** — all secondary-sales tables
- **fk_grocery, blinkit_truck_loading**

All show the first 8 columns in list view; full row accessible via "detail".
No create/edit/delete buttons — these tables are loaded by the external
uploader, Django-style.

---

## 5. How auth works under the hood

- **Session cookies** (not JWT) for the admin panel — standard Django-admin
  pattern. Signed with `JWT_SECRET` (via `SessionMiddleware`).
- The existing **JWT auth at `/api/auth/*`** is unchanged. Frontend still uses
  JWT; admin uses cookies. They coexist.
- `/admin/*` requests require `admin_user_id` in the session and the user
  must still be `is_superuser` + `is_active` on every page load (so you can
  instantly revoke admin access by unchecking `is_superuser`).

---

## 6. Common tasks

### Disable a user without deleting them
1. Users → click the user → untick **is_active** → save.
   They immediately can't log in anywhere (admin or frontend).

### Promote a regular user to admin
1. Users → click the user → tick **is_superuser** + **is_active** → save.

### Hide a platform from the frontend
1. Platforms → click the slug → untick **is_active** → save.
   Within 30 s the `/api/platform/{slug}/*` endpoints will 404 for that slug.

### Reset someone's password from admin
1. Users → click the user → type a new plaintext password in the
   **password_hash** field → save. The form handler hashes it automatically.

### Add a new platform (e.g. Meesho)
1. Platforms → "+ New Platform" → fill slug/name/tables/match_column.
2. Add the frontend entry in `frontend/src/config/platforms.js` too (that
   file is still hardcoded; keeping the table names in sync is your job).

---

## 7. Files added

- [db/sqlalchemy_db.py](db/sqlalchemy_db.py) — SQLAlchemy engine + Session
- [models/app_models.py](models/app_models.py) — User, TruckDispatch, PlatformConfig
- [models/warehouse.py](models/warehouse.py) — reflected read-only models
- [admin/auth.py](admin/auth.py) — cookie-based AuthenticationBackend
- [admin/views.py](admin/views.py) — ModelView configs
- [admin/setup.py](admin/setup.py) — mounts sqladmin into the FastAPI app
- [scripts/create_superuser.py](scripts/create_superuser.py) — CLI
- Modified [db/schema.py](db/schema.py) — adds columns + new table + seed
- Modified [routes/platform.py](routes/platform.py) — loads from DB with 30 s cache
- Modified [main.py](main.py) — SessionMiddleware + `mount_admin(app)`

---

## 8. Troubleshooting

### "Invalid credentials" on login
- Does the user exist? `SELECT id, email, is_superuser, is_active FROM users WHERE email='x';`
- `is_superuser` must be `TRUE`.
- `is_active` must be `TRUE`.
- Password: if you set it outside the admin, it must be in `salt:sha256hex`
  format. Use `python -m scripts.create_superuser` to fix.

### Admin loads but warehouse tables are missing from sidebar
- Check the uvicorn log — `[warehouse] could not reflect <table>: …` messages
  mean the Postgres user `dev01` can't see that table (permission) or the
  name is wrong. Fix and restart.

### Platform config changes don't apply
- 30 s cache. Wait half a minute or restart uvicorn for instant effect.

### SessionMiddleware errors at startup
- Make sure `JWT_SECRET` is set in `.env` — `SessionMiddleware` needs a secret.
