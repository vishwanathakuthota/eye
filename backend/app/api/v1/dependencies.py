from __future__ import annotations

from app.services.domain_intelligence import DomainIntelligenceService


def get_domain_intelligence_service() -> DomainIntelligenceService:
    return DomainIntelligenceService()
