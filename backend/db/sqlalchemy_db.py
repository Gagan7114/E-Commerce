"""
SQLAlchemy engine + session — used by the sqladmin admin panel.
Shares Postgres credentials with the psycopg2 pool; they coexist safely.
"""

from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD


# quote_plus protects `@`, `:`, `/` inside the password.
DATABASE_URL = (
    f"postgresql+psycopg2://{quote_plus(PG_USER)}:{quote_plus(PG_PASSWORD)}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all admin-managed models."""
    pass
