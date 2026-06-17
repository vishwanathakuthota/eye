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
        failed_sources = [source for source in sources if source.status == "failed"]
        rdap_state = "available" if rdap else "unavailable"
        certificate_state = (
            "Certificate transparency data could not be retrieved."
            if _source_failed("crt.sh", sources)
            else f"The analysis found {len(certificates)} certificate transparency entries."
        )
        failed_source_state = (
            " Failed sources: "
            + ", ".join(
                f"{source.name} ({source.error or source.error_type or 'unavailable'})"
                for source in failed_sources
            )
            + "."
            if failed_sources
            else ""
        )

        return (
            f"{domain} was analyzed using passive Domain Intelligence sources. "
            f"The analysis found {record_count} DNS records and {len(subdomains)} unique "
            f"subdomains. {certificate_state} "
            f"RDAP data is {rdap_state}. Risk is {risk.level} ({risk.score}/100). "
            f"Source status: {source_status}.{failed_source_state}"
        )


def _source_failed(name: str, sources: list[SourceStatusItem]) -> bool:
    return any(source.name == name and source.status == "failed" for source in sources)
