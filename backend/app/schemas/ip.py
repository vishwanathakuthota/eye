from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.domain import RiskResult, SourceStatusItem


class ReverseDnsFindings(BaseModel):
    ptr_records: list[str] = Field(default_factory=list)


class NetworkEnrichment(BaseModel):
    asn: str | None = None
    organization: str | None = None
    network: str | None = None
    classification: str
    source: str = "local-placeholder"
    note: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class IpAnalysisResult(BaseModel):
    report_id: str
    ip: str
    ip_version: int
    risk: RiskResult
    summary: str
    reverse_dns: ReverseDnsFindings
    network: NetworkEnrichment
    sources: list[SourceStatusItem]
    created_at: datetime
