from __future__ import annotations

import logging
from typing import Any

import httpx

from app.schemas.domain import CertificateFinding, SourceErrorType, SourceStatusItem
from app.services.retry import retry_call

logger = logging.getLogger(__name__)


class CrtShLookupService:
    def __init__(
        self,
        base_url: str = "https://crt.sh/",
        timeout_seconds: float = 12.0,
        max_results: int = 100,
    ) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_results = max_results

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
        except httpx.TimeoutException:
            logger.warning(
                "crtsh_lookup_timeout",
                extra={"domain": domain, "source": "crt.sh"},
            )
            return (
                [],
                [],
                _source_failure(
                    error_type="timeout",
                    error="Certificate transparency data could not be retrieved.",
                ),
            )
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.warning(
                "crtsh_lookup_http_error",
                extra={
                    "domain": domain,
                    "source": "crt.sh",
                    "status_code": status_code,
                },
            )
            return (
                [],
                [],
                _source_failure(
                    error_type=_classify_status_code(status_code),
                    error=_message_for_status_code(status_code),
                    status_code=status_code,
                ),
            )
        except httpx.HTTPError:
            logger.warning("crtsh_lookup_failed", extra={"domain": domain, "source": "crt.sh"})
            return (
                [],
                [],
                _source_failure(
                    error_type="unexpected_error",
                    error="Certificate transparency data could not be retrieved.",
                ),
            )
        except ValueError:
            logger.warning(
                "crtsh_lookup_invalid_response",
                extra={"domain": domain, "source": "crt.sh"},
            )
            return (
                [],
                [],
                _source_failure(
                    error_type="invalid_response",
                    error="Certificate transparency response was not valid JSON.",
                ),
            )

        if not isinstance(payload, list):
            return (
                [],
                [],
                _source_failure(
                    error_type="invalid_response",
                    error="Certificate transparency response had an unexpected shape.",
                ),
            )

        certificates = self._normalize_certificates(payload, max_results=self._max_results)
        subdomains = self._extract_subdomains(domain, certificates)
        source_status = SourceStatusItem(name="crt.sh", status="completed")
        if len(payload) > self._max_results:
            source_status = SourceStatusItem(
                name="crt.sh",
                status="partial",
                error=f"Certificate transparency results capped at {self._max_results}.",
            )
        return certificates, subdomains, source_status

    @staticmethod
    def _normalize_certificates(
        payload: list[Any],
        *,
        max_results: int,
    ) -> list[CertificateFinding]:
        seen: set[tuple[str, str | None, str | None]] = set()
        certificates: list[CertificateFinding] = []
        for item in payload:
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
            if len(certificates) >= max_results:
                break
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


def _source_failure(
    *,
    error_type: SourceErrorType,
    error: str,
    status_code: int | None = None,
) -> SourceStatusItem:
    return SourceStatusItem(
        name="crt.sh",
        status="failed",
        error=error,
        error_type=error_type,
        status_code=status_code,
    )


def _classify_status_code(status_code: int) -> SourceErrorType:
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "server_error"
    return "http_error"


def _message_for_status_code(status_code: int) -> str:
    if status_code == 404:
        return "Certificate transparency data was not found."
    if status_code == 429:
        return "Certificate transparency source rate limited the request."
    if status_code >= 500:
        return "Certificate transparency source returned a server error."
    return f"Certificate transparency source returned HTTP {status_code}."
