from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address

from app.schemas.domain import SourceStatusItem
from app.schemas.ip import NetworkEnrichment


class IpNetworkEnrichmentService:
    def enrich(
        self,
        ip_address: IPv4Address | IPv6Address,
    ) -> tuple[NetworkEnrichment, SourceStatusItem]:
        enrichment = NetworkEnrichment(
            classification=_classification_for(ip_address),
            note="ASN and ownership enrichment are placeholders until a passive source is added.",
            attributes={
                "is_global": ip_address.is_global,
                "is_private": ip_address.is_private,
                "is_reserved": ip_address.is_reserved,
                "is_loopback": ip_address.is_loopback,
                "is_multicast": ip_address.is_multicast,
                "is_link_local": ip_address.is_link_local,
                "reverse_pointer": ip_address.reverse_pointer,
            },
        )
        return enrichment, SourceStatusItem(name="network_enrichment", status="completed")


def _classification_for(ip_address: IPv4Address | IPv6Address) -> str:
    if ip_address.is_loopback:
        return "loopback"
    if ip_address.is_link_local:
        return "link_local"
    if ip_address.is_multicast:
        return "multicast"
    if ip_address.is_private:
        return "private"
    if ip_address.is_reserved:
        return "reserved"
    if ip_address.is_global:
        return "global"
    return "special_use"
