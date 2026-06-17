from __future__ import annotations

from app.services.domain_intelligence import DomainIntelligenceService
from app.services.ip_intelligence import IpIntelligenceService


def get_domain_intelligence_service() -> DomainIntelligenceService:
    return DomainIntelligenceService()


def get_ip_intelligence_service() -> IpIntelligenceService:
    return IpIntelligenceService()
