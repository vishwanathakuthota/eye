from __future__ import annotations

import logging
from typing import Any

import httpx

from app.schemas.domain import CertificateFinding, SourceStatusItem
from app.services.retry import retry_call

logger = logging.getLogger(__name__)


class CrtShLookupService:
    def __init__(self, base_url: str = "https://crt.sh/", timeout_seconds: float = 8.0) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def lookup(self, domain: str) -> tuple[list[CertificateFinding], list[str], SourceStatusItem]:
        params = {"q": f"%.{domain}", "output": "json"}
        try:
            response = retry_call(
                lambda: httpx.get(self._base_url, params=params, timeout=self._timeout_seconds),
                attempts=2,
                delay_seconds=0.5,
                source="crt.sh",
                retry_exceptions=(httpx.HTTPError,),
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("crtsh_lookup_failed", extra={"domain": domain, "source": "crt.sh"})
            return (
                [],
                [],
                SourceStatusItem(name="crt.sh", status="failed", error=exc.__class__.__name__),
            )

        if not isinstance(payload, list):
            return (
                [],
                [],
                SourceStatusItem(
                    name="crt.sh", status="failed", error="Unexpected response shape."
                ),
            )

        certificates = self._normalize_certificates(payload)
        subdomains = self._extract_subdomains(domain, certificates)
        return certificates, subdomains, SourceStatusItem(name="crt.sh", status="completed")

    @staticmethod
    def _normalize_certificates(payload: list[Any]) -> list[CertificateFinding]:
        seen: set[tuple[str, str | None, str | None]] = set()
        certificates: list[CertificateFinding] = []
        for item in payload[:100]:
            if not isinstance(item, dict) or not item.get("name_value"):
                continue
            finding = CertificateFinding(
                common_name=item.get("common_name"),
                name_value=str(item["name_value"]),
                issuer_name=item.get("issuer_name"),
                not_before=item.get("not_before"),
                not_after=item.get("not_after"),
            )
            key = (finding.name_value, finding.not_before, finding.not_after)
            if key in seen:
                continue
            seen.add(key)
            certificates.append(finding)
        return certificates

    @staticmethod
    def _extract_subdomains(domain: str, certificates: list[CertificateFinding]) -> list[str]:
        subdomains: set[str] = set()
        suffix = f".{domain}"
        for certificate in certificates:
            for name in certificate.name_value.splitlines():
                normalized = name.strip().lower().lstrip("*.").rstrip(".")
                if normalized == domain or not normalized.endswith(suffix):
                    continue
                subdomains.add(normalized)
        return sorted(subdomains)
