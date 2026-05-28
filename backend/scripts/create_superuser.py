"""
Create (or promote) an admin user.

Usage (from the backend/ folder with venv active):

    python -m scripts.create_superuser
    python -m scripts.create_superuser --email admin@jivo.in --password secret
"""

import argparse
import getpass
import sys
from pathlib import Path

# Make `backend/` importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.schema import ensure_schema  # noqa: E402
from db.sqlalchemy_db import SessionLocal  # noqa: E402
from models.app_models import User  # noqa: E402
from routes.auth import _hash_password  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Create or promote a superuser.")
    parser.add_argument("--email", help="Email (will be lowercased)")
    parser.add_argument("--password", help="Password (prompted if omitted)")
    args = parser.parse_args()

    ensure_schema()

    email = (args.email or input("Email: ")).strip().lower()
    if not email:
        sys.exit("email is required")

    password = args.password
    if not password:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Password (again): ")
        if password != confirm:
            sys.exit("passwords did not match")
    if len(password) < 6:
        sys.exit("password must be at least 6 characters")

    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = _hash_password(password)
            user.is_superuser = True
            user.is_active = True
            session.commit()
            print(f"Promoted existing user {email} to superuser.")
        else:
            user = User(
                email=email,
                password_hash=_hash_password(password),
                is_superuser=True,
                is_active=True,
            )
            session.add(user)
            session.commit()
            print(f"Created superuser {email} (id={user.id}).")


if __name__ == "__main__":
    main()
