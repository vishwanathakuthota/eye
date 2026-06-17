from __future__ import annotations

import logging

import dns.exception
import dns.resolver

from app.schemas.domain import EmailSecurityPosture, SourceStatusItem
from app.services.retry import retry_call

logger = logging.getLogger(__name__)


class EmailSecurityService:
    def __init__(self, timeout_seconds: float = 3.0, attempts: int = 2) -> None:
        self._timeout_seconds = timeout_seconds
        self._attempts = attempts

    def evaluate(
        self,
        domain: str,
        txt_records: list[str],
    ) -> tuple[EmailSecurityPosture, SourceStatusItem]:
        spf_record = next(
            (record for record in txt_records if record.lower().startswith("v=spf1")),
            None,
        )
        dmarc_record, dmarc_source = self._lookup_dmarc(domain)

        findings: list[str] = []
        recommendations: list[str] = []
        score = 100

        if spf_record:
            findings.append("SPF record is present.")
        else:
            score -= 35
            findings.append("SPF record was not found.")
            recommendations.append("Publish an SPF TXT record for authorized mail senders.")

        if dmarc_record:
            findings.append("DMARC record is present.")
            if "p=none" in dmarc_record.lower():
                score -= 15
                recommendations.append("Move DMARC policy toward quarantine or reject.")
        else:
            score -= 35
            findings.append("DMARC record was not found.")
            recommendations.append("Publish a DMARC TXT record at _dmarc.")

        recommendations.append("Review DKIM selectors with known mail providers.")

        posture = EmailSecurityPosture(
            spf_present=spf_record is not None,
            spf_record=spf_record,
            dmarc_present=dmarc_record is not None,
            dmarc_record=dmarc_record,
            dkim_status="placeholder",
            score=max(score, 0),
            findings=findings,
            recommendations=recommendations,
        )
        return posture, dmarc_source

    def _lookup_dmarc(self, domain: str) -> tuple[str | None, SourceStatusItem]:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = self._timeout_seconds
        resolver.timeout = self._timeout_seconds
        dmarc_domain = f"_dmarc.{domain}"

        try:
            answer = retry_call(
                lambda: resolver.resolve(dmarc_domain, "TXT"),
                attempts=self._attempts,
                delay_seconds=0.2,
                source="email_security",
                retry_exceptions=(dns.exception.DNSException,),
            )
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return None, SourceStatusItem(name="email_security", status="completed")
        except dns.exception.Timeout:
            logger.warning("dmarc_lookup_timeout", extra={"domain": domain, "source": "email"})
            return None, SourceStatusItem(
                name="email_security",
                status="partial",
                error="DMARC lookup timed out.",
                error_type="timeout",
            )
        except dns.exception.DNSException:
            logger.warning("dmarc_lookup_failed", extra={"domain": domain, "source": "email"})
            return None, SourceStatusItem(
                name="email_security",
                status="partial",
                error="DMARC lookup failed.",
                error_type="unexpected_error",
            )

        for item in answer:
            parts = getattr(item, "strings", [])
            value = "".join(part.decode("utf-8", errors="replace") for part in parts)
            if value.lower().startswith("v=dmarc1"):
                return value, SourceStatusItem(name="email_security", status="completed")

        return None, SourceStatusItem(name="email_security", status="completed")
