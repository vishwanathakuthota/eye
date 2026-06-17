from __future__ import annotations

from app.schemas.domain import RiskResult, SourceStatusItem
from app.schemas.ip import NetworkEnrichment, ReverseDnsFindings


class IpSummaryService:
    def generate(
        self,
        *,
        ip: str,
        ip_version: int,
        reverse_dns: ReverseDnsFindings,
        network: NetworkEnrichment,
        risk: RiskResult,
        sources: list[SourceStatusItem],
    ) -> str:
        source_status = ", ".join(f"{source.name}:{source.status}" for source in sources)
        ptr_state = (
            f"{len(reverse_dns.ptr_records)} PTR record(s) were found"
            if reverse_dns.ptr_records
            else "No PTR records were found"
        )

        return (
            f"{ip} was analyzed as an IPv{ip_version} address using passive IP Intelligence. "
            f"{ptr_state}. The address is classified as {network.classification}. "
            f"ASN and network ownership enrichment are placeholders in this milestone. "
            f"Risk is {risk.level} ({risk.score}/100). Source status: {source_status}."
        )
