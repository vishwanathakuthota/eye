from __future__ import annotations

import logging
from typing import Any

import httpx

from app.schemas.domain import SourceErrorType, SourceStatusItem
from app.services.retry import retry_call

logger = logging.getLogger(__name__)


class RdapLookupService:
    def __init__(
        self, base_url: str = "https://rdap.org/domain", timeout_seconds: float = 5.0
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def lookup(self, domain: str) -> tuple[dict[str, Any], SourceStatusItem]:
        url = f"{self._base_url}/{domain}"
        try:
            response = retry_call(
                lambda: httpx.get(url, timeout=self._timeout_seconds),
                attempts=2,
                delay_seconds=0.5,
                source="rdap",
                retry_exceptions=(httpx.HTTPError,),
            )
            if response.status_code == 404:
                return {}, SourceStatusItem(
                    name="rdap",
                    status="failed",
                    error="RDAP record not found.",
                    error_type="not_found",
                    status_code=response.status_code,
                )
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException:
            logger.warning(
                "rdap_lookup_timeout",
                extra={"domain": domain, "source": "rdap"},
            )
            return {}, _source_failure(error_type="timeout", error="RDAP lookup timed out.")
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            error_type = _classify_status_code(status_code)
            logger.warning(
                "rdap_lookup_http_error",
                extra={
                    "domain": domain,
                    "source": "rdap",
                    "status_code": status_code,
                },
            )
            return (
                {},
                _source_failure(
                    error_type=error_type,
                    error=_message_for_status_code(status_code),
                    status_code=status_code,
                ),
            )
        except httpx.HTTPError:
            logger.warning("rdap_lookup_failed", extra={"domain": domain, "source": "rdap"})
            return {}, _source_failure(
                error_type="unexpected_error",
                error="RDAP lookup failed.",
            )
        except ValueError:
            logger.warning(
                "rdap_lookup_invalid_response",
                extra={"domain": domain, "source": "rdap"},
            )
            return {}, _source_failure(
                error_type="invalid_response",
                error="RDAP response was not valid JSON.",
            )

        return self._normalize(payload), SourceStatusItem(name="rdap", status="completed")

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "handle": payload.get("handle"),
            "ldh_name": payload.get("ldhName"),
            "status": payload.get("status", []),
            "events": payload.get("events", []),
            "nameservers": payload.get("nameservers", []),
            "registrar": _extract_registrar(payload),
        }


def _extract_registrar(payload: dict[str, Any]) -> str | None:
    for entity in payload.get("entities", []):
        roles = entity.get("roles", [])
        if "registrar" not in roles:
            continue
        vcard = entity.get("vcardArray", [])
        if len(vcard) < 2:
            return entity.get("handle")
        for item in vcard[1]:
            if item and item[0] == "fn" and len(item) >= 4:
                return item[3]
    return None


def _source_failure(
    *,
    error_type: SourceErrorType,
    error: str,
    status_code: int | None = None,
) -> SourceStatusItem:
    return SourceStatusItem(
        name="rdap",
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
        return "RDAP record not found."
    if status_code == 429:
        return "RDAP source rate limited the request."
    if status_code >= 500:
        return "RDAP source returned a server error."
    return f"RDAP source returned HTTP {status_code}."
