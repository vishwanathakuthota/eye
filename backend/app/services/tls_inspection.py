from __future__ import annotations

import logging
import socket
import ssl
from datetime import UTC, datetime

from app.schemas.domain import SourceStatusItem, TlsCertificateInfo

logger = logging.getLogger(__name__)


class TlsInspectionService:
    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self._timeout_seconds = timeout_seconds

    def inspect(self, domain: str) -> tuple[TlsCertificateInfo | None, SourceStatusItem]:
        context = ssl.create_default_context()
        try:
            with socket.create_connection((domain, 443), timeout=self._timeout_seconds) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as tls_socket:
                    certificate = tls_socket.getpeercert()
        except TimeoutError:
            logger.warning("tls_inspection_timeout", extra={"domain": domain, "source": "tls"})
            return None, SourceStatusItem(
                name="tls",
                status="failed",
                error="TLS certificate inspection timed out.",
                error_type="timeout",
            )
        except (OSError, ssl.SSLError):
            logger.warning("tls_inspection_failed", extra={"domain": domain, "source": "tls"})
            return None, SourceStatusItem(
                name="tls",
                status="failed",
                error="TLS certificate could not be retrieved.",
                error_type="unexpected_error",
            )

        info = _certificate_info(domain, certificate)
        return info, SourceStatusItem(name="tls", status="completed")


def _certificate_info(domain: str, certificate: dict[str, object]) -> TlsCertificateInfo:
    valid_from = _parse_certificate_date(certificate.get("notBefore"))
    valid_to = _parse_certificate_date(certificate.get("notAfter"))
    days_remaining = None
    findings: list[str] = []
    recommendations: list[str] = []
    status = "unknown"

    if valid_to is not None:
        days_remaining = (valid_to - datetime.now(UTC)).days
        if days_remaining < 0:
            status = "expired"
            findings.append("TLS certificate is expired.")
            recommendations.append("Renew the TLS certificate immediately.")
        elif days_remaining <= 14:
            status = "expiring_soon"
            findings.append("TLS certificate expires within 14 days.")
            recommendations.append("Renew the TLS certificate soon.")
        else:
            status = "valid"
            findings.append("TLS certificate is currently valid.")

    return TlsCertificateInfo(
        checked_host=domain,
        issuer=_name_to_string(certificate.get("issuer")),
        subject=_name_to_string(certificate.get("subject")),
        valid_from=valid_from.isoformat() if valid_from else None,
        valid_to=valid_to.isoformat() if valid_to else None,
        days_remaining=days_remaining,
        status=status,
        findings=findings,
        recommendations=recommendations,
    )


def _parse_certificate_date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
    except ValueError:
        return None


def _name_to_string(value: object) -> str | None:
    if not isinstance(value, tuple):
        return None
    parts: list[str] = []
    for group in value:
        if not isinstance(group, tuple):
            continue
        for item in group:
            if isinstance(item, tuple) and len(item) == 2:
                parts.append(f"{item[0]}={item[1]}")
    return ", ".join(parts) if parts else None
