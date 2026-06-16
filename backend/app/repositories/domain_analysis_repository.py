from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.domain_analysis import DomainAnalysis
from app.schemas.domain import DomainAnalysisResult


class DomainAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, result: DomainAnalysisResult) -> DomainAnalysis:
        record = DomainAnalysis(
            report_id=result.report_id,
            domain=result.domain,
            risk_score=result.risk.score,
            risk_level=result.risk.level,
            summary=result.summary,
            dns=result.dns.model_dump(mode="json"),
            rdap=result.rdap,
            certificates=[
                certificate.model_dump(mode="json") for certificate in result.certificates
            ],
            subdomains=result.subdomains,
            sources=[source.model_dump(mode="json") for source in result.sources],
            created_at=result.created_at,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record
