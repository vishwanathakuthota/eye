from __future__ import annotations

from app.schemas.domain import RiskResult, SourceStatusItem
from app.schemas.ip import NetworkEnrichment, ReverseDnsFindings


class IpRiskScoringService:
    def score(
        self,
        *,
        reverse_dns: ReverseDnsFindings,
        network: NetworkEnrichment,
        sources: list[SourceStatusItem],
    ) -> RiskResult:
        score = 0
        reasons: list[str] = []
        confidence = 100
        reliability_notes: list[str] = []

        if network.classification in {"loopback", "link_local", "multicast"}:
            score += 25
            reasons.append(f"IP address is classified as {network.classification}.")
        elif network.classification in {"private", "reserved", "special_use"}:
            score += 15
            reasons.append(f"IP address is classified as {network.classification}.")

        if not reverse_dns.ptr_records and _source_completed("reverse_dns", sources):
            score += 5
            reasons.append("No reverse DNS PTR records were found.")

        for source in sources:
            if source.status == "failed":
                confidence -= 10
                reliability_notes.append(
                    f"{source.name} source reliability issue: "
                    f"{(source.error or 'unavailable').rstrip('.')}."
                )

        normalized_score = min(score, 100)
        return RiskResult(
            score=normalized_score,
            level=self._level_for_score(normalized_score),
            reasons=reasons,
            confidence=max(confidence, 0),
            reliability_notes=reliability_notes,
        )

    @staticmethod
    def _level_for_score(score: int) -> str:
        if score >= 75:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 25:
            return "Medium"
        return "Low"


def _source_completed(name: str, sources: list[SourceStatusItem]) -> bool:
    return any(source.name == name and source.status == "completed" for source in sources)
