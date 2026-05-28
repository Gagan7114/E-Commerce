"""
Assign a user to one or more groups.

Usage:
    python -m scripts.assign_user_to_group --email ops@jivo.in --group "Operations Manager"
    python -m scripts.assign_user_to_group --email viewer@jivo.in --group "Viewer" --group "Finance Analyst"
    python -m scripts.assign_user_to_group --email ops@jivo.in --clear   # remove all groups
    python -m scripts.assign_user_to_group --list                        # show every user's groups
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.sqlalchemy_db import SessionLocal  # noqa: E402
from models.app_models import User  # noqa: E402
from models.permissions import Group  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="User email")
    parser.add_argument("--group", action="append", default=[], help="Group name (repeatable)")
    parser.add_argument("--clear", action="store_true", help="Remove the user from all groups")
    parser.add_argument("--list", action="store_true", help="Print users and their groups, then exit")
    args = parser.parse_args()

    with SessionLocal() as session:
        if args.list:
            for u in session.query(User).order_by(User.id).all():
                names = ", ".join(g.name for g in u.groups) or "(no groups)"
                flags = " [superuser]" if u.is_superuser else ""
                print(f"  {u.id:3d}  {u.email}{flags}  ->  {names}")
            return

        if not args.email:
            sys.exit("--email is required (or use --list)")

        user = session.query(User).filter(User.email == args.email.strip().lower()).first()
        if not user:
            sys.exit(f"no user with email {args.email!r}")

        if args.clear:
            user.groups = []
        elif args.group:
            groups = []
            for gname in args.group:
                g = session.query(Group).filter(Group.name == gname).first()
                if not g:
                    sys.exit(f"no group named {gname!r}. Run `python -m scripts.seed_permissions` first?")
                groups.append(g)
            user.groups = groups
        else:
            sys.exit("nothing to do: pass --group, --clear, or --list")

        session.commit()
        final = ", ".join(g.name for g in user.groups) or "(no groups)"
        print(f"{user.email} -> {final}")


if __name__ == "__main__":
    main()
