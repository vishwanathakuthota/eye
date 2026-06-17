from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["Low", "Medium", "High", "Critical"]
SourceStatus = Literal["completed", "partial", "failed"]
SourceErrorType = Literal[
    "not_found",
    "timeout",
    "rate_limited",
    "server_error",
    "http_error",
    "invalid_response",
    "unexpected_error",
]


class SourceStatusItem(BaseModel):
    name: str
    status: SourceStatus
    error: str | None = None
    error_type: SourceErrorType | None = None
    status_code: int | None = None


class DnsRecordSet(BaseModel):
    A: list[str] = Field(default_factory=list)
    AAAA: list[str] = Field(default_factory=list)
    MX: list[str] = Field(default_factory=list)
    TXT: list[str] = Field(default_factory=list)
    NS: list[str] = Field(default_factory=list)
    CNAME: list[str] = Field(default_factory=list)


class DnsFindings(BaseModel):
    records: DnsRecordSet = Field(default_factory=DnsRecordSet)


class CertificateFinding(BaseModel):
    common_name: str | None = None
    name_value: str
    issuer_name: str | None = None
    not_before: str | None = None
    not_after: str | None = None


class RiskResult(BaseModel):
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    reasons: list[str] = Field(default_factory=list)
    confidence: int = Field(default=100, ge=0, le=100)
    reliability_notes: list[str] = Field(default_factory=list)


class DomainAnalysisResult(BaseModel):
    report_id: str
    domain: str
    risk: RiskResult
    summary: str
    dns: DnsFindings
    rdap: dict[str, Any]
    certificates: list[CertificateFinding]
    subdomains: list[str]
    sources: list[SourceStatusItem]
    created_at: datetime
