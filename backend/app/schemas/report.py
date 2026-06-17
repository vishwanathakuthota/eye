from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.domain import DomainAnalysisResult, RiskLevel
from app.schemas.ip import IpAnalysisResult

ReportType = Literal["domain", "ip"]


class ReportSummary(BaseModel):
    report_id: str
    type: ReportType
    target: str
    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    created_at: datetime


class ReportListResult(BaseModel):
    items: list[ReportSummary]
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class ReportDetailResult(BaseModel):
    report_id: str
    type: ReportType
    target: str
    payload: DomainAnalysisResult | IpAnalysisResult
