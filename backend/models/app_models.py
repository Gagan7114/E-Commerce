"""Declarative models for app-owned tables: users, truck_dispatches, platform_config."""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.sqlalchemy_db import Base
from models.permissions import Group, Permission, user_groups, user_permissions


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True)
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_superuser  = Column(Boolean, default=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())

    groups = relationship(Group, secondary=user_groups, backref="users", lazy="selectin")
    direct_permissions = relationship(
        Permission, secondary=user_permissions, backref="direct_users", lazy="selectin"
    )

    def __str__(self):
        flag = " [superuser]" if self.is_superuser else ""
        return f"{self.email}{flag}"

    def all_permission_codes(self):
        """Flatten group perms + direct perms into one set of permission codes."""
        codes = {p.code for p in self.direct_permissions}
        for g in self.groups:
            for p in g.permissions:
                codes.add(p.code)
        return codes


class TruckDispatch(Base):
    __tablename__ = "truck_dispatches"

    id              = Column(Integer, primary_key=True)
    platform_slug   = Column(String(32), nullable=False, index=True)
    platform        = Column(String(64))
    mode            = Column(String(16))
    truck_type      = Column(String(32))
    capacity_kg     = Column(Numeric)
    loaded_kg       = Column(Numeric)
    fill_percentage = Column(Numeric)
    po_count        = Column(Integer)
    po_details      = Column(JSONB)
    status          = Column(String(32), default="dispatched")
    dispatch_date   = Column(Date)
    dispatch_time   = Column(String(8))
    vehicle_number  = Column(String(32))
    driver_name     = Column(String(100))
    driver_phone    = Column(String(15))
    notes           = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return f"[{self.platform_slug}] {self.vehicle_number} · {self.po_count} POs"


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    slug             = Column(String(32), primary_key=True)
    name             = Column(String(64), nullable=False)
    inventory_table  = Column(String(64), nullable=False)
    secondary_table  = Column(String(64), nullable=False)
    master_po_table  = Column(String(64), nullable=False, default="master_po")
    po_filter_column = Column(String(64), nullable=False, default="format")
    po_filter_value  = Column(String(64), nullable=False)
    match_column     = Column(String(64), nullable=False)
    is_active        = Column(Boolean, nullable=False, default=True)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return f"{self.name} ({self.slug})"
