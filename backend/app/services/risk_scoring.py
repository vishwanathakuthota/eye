from __future__ import annotations

from app.schemas.domain import CertificateFinding, DnsFindings, RiskResult, SourceStatusItem


class RiskScoringService:
    def score(
        self,
        *,
        dns: DnsFindings,
        rdap: dict[str, object],
        certificates: list[CertificateFinding],
        subdomains: list[str],
        sources: list[SourceStatusItem],
    ) -> RiskResult:
        score = 0
        reasons: list[str] = []

        if not any(dns.records.model_dump().values()):
            score += 25
            reasons.append("No DNS records were discovered.")

        if not rdap:
            score += 15
            reasons.append("RDAP registration data was unavailable.")

        failed_sources = [source.name for source in sources if source.status == "failed"]
        if failed_sources:
            score += min(20, 8 * len(failed_sources))
            reasons.append(f"Source failures: {', '.join(failed_sources)}.")

        if len(subdomains) > 25:
            score += 15
            reasons.append("Certificate transparency revealed more than 25 subdomains.")
        elif len(subdomains) > 10:
            score += 8
            reasons.append("Certificate transparency revealed more than 10 subdomains.")

        if not certificates:
            score += 10
            reasons.append("No certificate transparency entries were discovered.")

        normalized_score = min(score, 100)
        return RiskResult(
            score=normalized_score,
            level=self._level_for_score(normalized_score),
            reasons=reasons,
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
