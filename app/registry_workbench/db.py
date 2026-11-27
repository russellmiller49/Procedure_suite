"""Workbench storage: its own SQLite file and schema, separate from the v3 registry store.

Synthetic documents only. Revisions are append-only; a case points at its current
draft and approved revision, guarded by an optimistic-concurrency version.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timezone
from functools import lru_cache
from typing import Any, Iterator

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

DEFAULT_URL = "sqlite:///./registry_workbench.db"


def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Case(Base):
    __tablename__ = "wb_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    label: Mapped[str] = mapped_column(String(200), unique=True)
    family_id: Mapped[str | None] = mapped_column(String(64), index=True)
    platform: Mapped[str | None] = mapped_column(String(64))
    split: Mapped[str | None] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(200))
    event_date: Mapped[date | None] = mapped_column(Date)
    version: Mapped[int] = mapped_column(Integer, default=1)
    draft_revision_id: Mapped[str | None] = mapped_column(String(36))
    approved_revision_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Document(Base):
    __tablename__ = "wb_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    case_id: Mapped[str] = mapped_column(ForeignKey("wb_cases.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    corpus_document_id: Mapped[str | None] = mapped_column(String(64), index=True)
    variant: Mapped[str | None] = mapped_column(String(64))
    exposure: Mapped[str] = mapped_column(String(32), default="development")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExtractionRun(Base):
    __tablename__ = "wb_extraction_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("wb_documents.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str | None] = mapped_column(String(64))
    effort: Mapped[str | None] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="queued")
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)
    prompt_digest: Mapped[str | None] = mapped_column(String(64))
    schema_digest: Mapped[str | None] = mapped_column(String(64))
    cost_usd: Mapped[float | None] = mapped_column(Float)
    latency_s: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Revision(Base):
    __tablename__ = "wb_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    case_id: Mapped[str] = mapped_column(ForeignKey("wb_cases.id"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[str | None] = mapped_column(String(36))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    payload_digest: Mapped[str] = mapped_column(String(64))
    mode: Mapped[str] = mapped_column(String(16))
    source_run_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Event(Base):
    __tablename__ = "wb_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    case_id: Mapped[str | None] = mapped_column(String(36), index=True)
    document_id: Mapped[str | None] = mapped_column(String(36), index=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


def database_url() -> str:
    return os.getenv("REGISTRY_WORKBENCH_DATABASE_URL") or DEFAULT_URL


@lru_cache(maxsize=4)
def engine_for(url: str) -> Engine:
    kwargs: dict[str, Any] = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(engine)
    return engine


@lru_cache(maxsize=4)
def _sessionmaker(url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=engine_for(url), autoflush=False, expire_on_commit=False)


def session_factory() -> sessionmaker[Session]:
    return _sessionmaker(database_url())


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, committed by the service layer."""
    db = session_factory()()
    try:
        yield db
    finally:
        db.close()


__all__ = [
    "Base",
    "Case",
    "Document",
    "Event",
    "ExtractionRun",
    "Revision",
    "database_url",
    "engine_for",
    "get_db",
    "session_factory",
]
