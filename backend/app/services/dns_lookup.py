from __future__ import annotations

import logging

import dns.exception
import dns.resolver

from app.schemas.domain import DnsFindings, DnsRecordSet, SourceStatusItem
from app.services.retry import retry_call

logger = logging.getLogger(__name__)

SUPPORTED_RECORD_TYPES = ("A", "AAAA", "MX", "TXT", "NS", "CNAME")


class DnsLookupService:
    def __init__(self, timeout_seconds: float = 3.0, attempts: int = 2) -> None:
        self._timeout_seconds = timeout_seconds
        self._attempts = attempts

    def lookup(self, domain: str) -> tuple[DnsFindings, SourceStatusItem]:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = self._timeout_seconds
        resolver.timeout = self._timeout_seconds

        records: dict[str, list[str]] = {record_type: [] for record_type in SUPPORTED_RECORD_TYPES}
        errors: list[str] = []

        for record_type in SUPPORTED_RECORD_TYPES:
            try:
                answer = retry_call(
                    lambda record_type=record_type: resolver.resolve(domain, record_type),
                    attempts=self._attempts,
                    delay_seconds=0.2,
                    source="dns",
                    retry_exceptions=(dns.exception.DNSException,),
                )
            except dns.resolver.NoAnswer:
                continue
            except dns.resolver.NXDOMAIN:
                errors.append(f"{record_type}: domain does not exist")
                logger.info("dns_lookup_nxdomain", extra={"domain": domain, "source": "dns"})
                break
            except dns.exception.DNSException as exc:
                errors.append(f"{record_type}: {exc.__class__.__name__}")
                logger.warning("dns_lookup_failed", extra={"domain": domain, "source": "dns"})
                continue

            records[record_type] = [self._format_answer(record_type, item) for item in answer]

        status = "completed"
        error = None
        if errors and any(records.values()):
            status = "partial"
            error = "; ".join(errors)
        elif errors:
            status = "failed"
            error = "; ".join(errors)

        return DnsFindings(records=DnsRecordSet(**records)), SourceStatusItem(
            name="dns",
            status=status,
            error=error,
        )

    @staticmethod
    def _format_answer(record_type: str, item: object) -> str:
        if record_type == "MX" and hasattr(item, "preference") and hasattr(item, "exchange"):
            return f"{item.preference} {item.exchange}".rstrip(".")
        if record_type == "TXT" and hasattr(item, "strings"):
            return "".join(part.decode("utf-8", errors="replace") for part in item.strings)
        return str(item).rstrip(".")
