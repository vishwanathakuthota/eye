from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class DomainAnalysis(Base):
    __tablename__ = "domain_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(253), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16))
    risk: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    dns: Mapped[dict[str, object]] = mapped_column(JSON)
    rdap: Mapped[dict[str, object]] = mapped_column(JSON)
    certificates: Mapped[list[dict[str, object]]] = mapped_column(JSON)
    subdomains: Mapped[list[str]] = mapped_column(JSON)
    sources: Mapped[list[dict[str, object]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
