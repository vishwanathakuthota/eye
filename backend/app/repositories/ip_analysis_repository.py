from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.ip_analysis import IpAnalysis
from app.schemas.ip import IpAnalysisResult


class IpAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, result: IpAnalysisResult) -> IpAnalysis:
        record = IpAnalysis(
            report_id=result.report_id,
            ip=result.ip,
            ip_version=result.ip_version,
            risk_score=result.risk.score,
            risk_level=result.risk.level,
            risk=result.risk.model_dump(mode="json"),
            summary=result.summary,
            reverse_dns=result.reverse_dns.model_dump(mode="json"),
            network=result.network.model_dump(mode="json"),
            sources=[source.model_dump(mode="json") for source in result.sources],
            created_at=result.created_at,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record
