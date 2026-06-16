from __future__ import annotations

import logging
from typing import Any

import httpx

from app.schemas.domain import SourceStatusItem
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
                    name="rdap", status="failed", error="RDAP record not found."
                )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("rdap_lookup_failed", extra={"domain": domain, "source": "rdap"})
            return {}, SourceStatusItem(name="rdap", status="failed", error=exc.__class__.__name__)

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
