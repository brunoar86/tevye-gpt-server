import enum
import uuid

from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, func, text,
    CHAR
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import (
    UUID as PG_UUID, ARRAY, ENUM as PG_ENUM, CITEXT, INET
)

from tevye_gpt_server.src.db.base import Base


class RoleEnum(str, enum.Enum):
    user = 'user'
    admin = 'admin'
    auditor = 'auditor'


class Tenant(Base):
    __tablename__ = 'tenants'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        CITEXT,
        unique=True,
        nullable=False
        )
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey('tenants.id', ondelete='SET NULL'),
        nullable=True
        )
    pwd_hash: Mapped[str] = mapped_column(Text, nullable=False)
    roles: Mapped[list[RoleEnum]] = mapped_column(
        ARRAY(PG_ENUM(RoleEnum, name='role_enum', create_type=False)),
        server_default=text("ARRAY['user']::role_enum[]"),
        nullable=False
        )
    token_version: Mapped[int] = mapped_column(
        Integer,
        server_default=text('0'),
        nullable=False
        )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text('true'),
        nullable=False
        )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
        )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
        )
    tenant: Mapped[Tenant | None] = relationship(backref='users')


class RefreshSession(Base):
    __tablename__ = 'refresh_sessions'

    __table_args__ = (
        UniqueConstraint('sid', name='uq_refresh_sid'),
        CheckConstraint('expires_at > created_at',
                        name='ck_refresh_exp_gt_created'),
        Index('ix_sessions_user_active', 'user_id', 'is_active'),
        Index('ix_sessions_expires_at', 'expires_at'),
        Index('ix_sessions_jti', 'jti')
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    sid: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        server_default=text('gen_random_uuid()')
    )
    jti: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        server_default=text('gen_random_uuid()'),
        index=True
    )
    refresh_hash: Mapped[str] = mapped_column(
        CHAR(64),
        nullable=False
    )
    user_agent_fingerprint: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )
    ip: Mapped[str] = mapped_column(
        INET,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('true')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
