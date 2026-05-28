"""
Sync the DB permissions/groups tables with the catalog defined in
backend/permissions.py.

Safe to run multiple times (idempotent):
  - Inserts any missing permission codes.
  - Inserts any missing default groups.
  - Syncs each group's permission set to exactly what the catalog declares.
  - Does NOT touch user_groups / user_permissions — user assignments are preserved.

Usage (from backend/ with venv active):

    python -m scripts.seed_permissions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.schema import ensure_schema  # noqa: E402
from db.sqlalchemy_db import SessionLocal  # noqa: E402
from models.permissions import Group, Permission  # noqa: E402
from permissions import PERMISSIONS, ROLES, _expand_patterns  # noqa: E402


def main():
    ensure_schema()

    with SessionLocal() as session:
        # 1. Upsert permissions
        existing_codes = {p.code: p for p in session.query(Permission).all()}
        for code, desc in PERMISSIONS:
            if code in existing_codes:
                if existing_codes[code].description != desc:
                    existing_codes[code].description = desc
            else:
                session.add(Permission(code=code, description=desc))
        session.flush()

        # Refresh cache of all permissions by code for quick lookup
        all_perms_by_code = {p.code: p for p in session.query(Permission).all()}

        # 2. Upsert groups + sync their permissions to the catalog
        for role_name, meta in ROLES.items():
            group = session.query(Group).filter(Group.name == role_name).first()
            if group is None:
                group = Group(name=role_name, description=meta["description"])
                session.add(group)
                session.flush()
            elif group.description != meta["description"]:
                group.description = meta["description"]

            desired_codes = _expand_patterns(meta["perms"])
            desired_perms = [all_perms_by_code[c] for c in desired_codes if c in all_perms_by_code]
            group.permissions = desired_perms  # replace M2M collection

        session.commit()

    # Summary
    with SessionLocal() as session:
        print("Permissions in DB:", session.query(Permission).count())
        for g in session.query(Group).order_by(Group.name).all():
            print(f"  Group {g.name!r:22s} — {len(g.permissions)} perms")


if __name__ == "__main__":
    main()
