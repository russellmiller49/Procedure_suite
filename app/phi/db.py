"""SQLAlchemy base and shared types for PHI models.

This module keeps ORM configuration scoped to PHI tables so we can
swap storage backends in future HIPAA deployments.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, String, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class GUID(TypeDecorator[uuid.UUID]):
    """Platform-independent GUID/UUID type for Postgres and SQLite."""

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: uuid.UUID | str | None, dialect: Dialect) -> str | uuid.UUID | None:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value if dialect.name == "postgresql" else str(value)
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> uuid.UUID | None:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


# Portable column types (JSONB/UUID for Postgres, JSON/String for SQLite)
UUIDType = GUID
JSONType = JSONB().with_variant(JSON(), "sqlite")

__all__ = ["Base", "metadata", "GUID", "UUIDType", "JSONType"]
