from __future__ import annotations

from app.schemas.domain import CertificateFinding, DnsFindings, RiskResult, SourceStatusItem


class IntelligenceSummaryService:
    def generate(
        self,
        *,
        domain: str,
        dns: DnsFindings,
        rdap: dict[str, object],
        certificates: list[CertificateFinding],
        subdomains: list[str],
        risk: RiskResult,
        sources: list[SourceStatusItem],
    ) -> str:
        record_count = sum(len(values) for values in dns.records.model_dump().values())
        source_status = ", ".join(f"{source.name}:{source.status}" for source in sources)
        rdap_state = "available" if rdap else "unavailable"

        return (
            f"{domain} was analyzed using passive Domain Intelligence sources. "
            f"The analysis found {record_count} DNS records, {len(certificates)} certificate "
            f"transparency entries, and {len(subdomains)} unique subdomains. "
            f"RDAP data is {rdap_state}. Risk is {risk.level} ({risk.score}/100). "
            f"Source status: {source_status}."
        )
