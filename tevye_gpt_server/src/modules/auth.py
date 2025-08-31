import enum
import uuid

from __future__ import annotations
from datetime import datetime
from sqlalchemy import (String, Text, Boolean, DateTime, ForeignKey, Index,
                        UniqueConstraint, CheckConstraint, func, text, CHAR)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, ENUM as PG_ENUM, CITEXT, INET


class Base(DeclarativeBase):
    pass


class RoleEnum(str, enum.Enum):
    user = 'user'
    admin = 'admin'
    auditor = 'auditor'


class Tenant(Base):
    __tablename__ = 'tenants'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
