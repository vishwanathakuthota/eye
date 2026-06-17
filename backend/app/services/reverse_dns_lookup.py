from __future__ import annotations

import logging
from ipaddress import IPv4Address, IPv6Address

import dns.exception
import dns.resolver
import dns.reversename

from app.schemas.domain import SourceStatusItem
from app.schemas.ip import ReverseDnsFindings
from app.services.retry import retry_call

logger = logging.getLogger(__name__)


class ReverseDnsLookupService:
    def __init__(self, timeout_seconds: float = 3.0, attempts: int = 2) -> None:
        self._timeout_seconds = timeout_seconds
        self._attempts = attempts

    def lookup(
        self,
        ip_address: IPv4Address | IPv6Address,
    ) -> tuple[ReverseDnsFindings, SourceStatusItem]:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = self._timeout_seconds
        resolver.timeout = self._timeout_seconds
        reverse_name = dns.reversename.from_address(str(ip_address))

        try:
            answer = retry_call(
                lambda: resolver.resolve(reverse_name, "PTR"),
                attempts=self._attempts,
                delay_seconds=0.5,
                source="reverse_dns",
                retry_exceptions=(dns.exception.DNSException,),
            )
        except dns.resolver.NXDOMAIN:
            logger.info("reverse_dns_nxdomain", extra={"source": "reverse_dns"})
            return ReverseDnsFindings(), SourceStatusItem(
                name="reverse_dns",
                status="completed",
                error="No PTR records were found.",
                error_type="not_found",
            )
        except dns.resolver.NoAnswer:
            logger.info("reverse_dns_no_answer", extra={"source": "reverse_dns"})
            return ReverseDnsFindings(), SourceStatusItem(
                name="reverse_dns",
                status="completed",
                error="No PTR records were found.",
                error_type="not_found",
            )
        except dns.exception.Timeout:
            logger.warning("reverse_dns_timeout", extra={"source": "reverse_dns"})
            return ReverseDnsFindings(), SourceStatusItem(
                name="reverse_dns",
                status="failed",
                error="Reverse DNS lookup timed out.",
                error_type="timeout",
            )
        except dns.exception.DNSException:
            logger.warning("reverse_dns_failed", extra={"source": "reverse_dns"})
            return ReverseDnsFindings(), SourceStatusItem(
                name="reverse_dns",
                status="failed",
                error="Reverse DNS lookup failed.",
                error_type="unexpected_error",
            )

        records = sorted({str(item).rstrip(".") for item in answer})
        return ReverseDnsFindings(ptr_records=records), SourceStatusItem(
            name="reverse_dns",
            status="completed",
        )
