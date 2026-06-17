from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["Low", "Medium", "High", "Critical"]
IntelligenceConfidence = Literal["High", "Medium", "Low"]
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


class IntelligenceSection(BaseModel):
    title: str
    body: str
    bullets: list[str] = Field(default_factory=list)


class EmailSecurityPosture(BaseModel):
    spf_present: bool = False
    spf_record: str | None = None
    dmarc_present: bool = False
    dmarc_record: str | None = None
    dkim_status: str = "not_checked"
    score: int = Field(default=0, ge=0, le=100)
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SecurityHeaderFinding(BaseModel):
    name: str
    present: bool
    value: str | None = None
    recommendation: str | None = None


class WebSecurityPosture(BaseModel):
    checked_url: str | None = None
    status_code: int | None = None
    headers: list[SecurityHeaderFinding] = Field(default_factory=list)
    score: int = Field(default=0, ge=0, le=100)
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TlsCertificateInfo(BaseModel):
    checked_host: str
    issuer: str | None = None
    subject: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    days_remaining: int | None = None
    status: str = "unknown"
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TechnologyFingerprint(BaseModel):
    server: str | None = None
    powered_by: str | None = None
    cdn_or_security: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class IntelligenceSummaryV2(BaseModel):
    executive_summary: IntelligenceSection
    attack_surface_snapshot: IntelligenceSection
    email_security: IntelligenceSection
    web_security: IntelligenceSection
    infrastructure: IntelligenceSection
    confidence_notes: IntelligenceSection
    recommendations: IntelligenceSection


class IntelligenceValueLayer(BaseModel):
    intelligence_confidence: IntelligenceConfidence = "High"
    incomplete_intelligence: bool = False
    confidence_notes: list[str] = Field(default_factory=list)
    email_security: EmailSecurityPosture = Field(default_factory=EmailSecurityPosture)
    web_security: WebSecurityPosture = Field(default_factory=WebSecurityPosture)
    tls: TlsCertificateInfo | None = None
    technology: TechnologyFingerprint = Field(default_factory=TechnologyFingerprint)
    recommendations: list[str] = Field(default_factory=list)
    summary_v2: IntelligenceSummaryV2 | None = None


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
    intelligence: IntelligenceValueLayer = Field(default_factory=IntelligenceValueLayer)
    created_at: datetime
