"""
SQLAlchemy models for the permission system.

Shape (Django-style):
  User  ─M:N─> Group  ─M:N─> Permission
  User  ─M:N─> Permission   (direct overrides)

Superusers (`users.is_superuser = TRUE`) bypass all permission checks.
Regular users accumulate the union of their group permissions + direct ones.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from db.sqlalchemy_db import Base


group_permissions = Table(
    "group_permissions",
    Base.metadata,
    Column("group_id",      Integer, ForeignKey("groups.id",      ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)

user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id",  Integer, ForeignKey("users.id",  ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)

user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id",       Integer, ForeignKey("users.id",       ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)


class Permission(Base):
    __tablename__ = "permissions"

    id          = Column(Integer, primary_key=True)
    code        = Column(String(64), unique=True, nullable=False)
    description = Column(String(200), default="")

    def __str__(self):
        return self.code


class Group(Base):
    __tablename__ = "groups"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(64), unique=True, nullable=False)
    description = Column(String(200), default="")

    permissions = relationship(
        Permission,
        secondary=group_permissions,
        backref="groups",
        lazy="selectin",
    )

    def __str__(self):
        return self.name
