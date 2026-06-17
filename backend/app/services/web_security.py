from __future__ import annotations

import logging

import httpx

from app.schemas.domain import (
    SecurityHeaderFinding,
    SourceStatusItem,
    TechnologyFingerprint,
    WebSecurityPosture,
)

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "strict-transport-security": "Enable HSTS to require HTTPS.",
    "content-security-policy": "Add a Content Security Policy to reduce injection risk.",
    "x-frame-options": "Set X-Frame-Options or CSP frame-ancestors.",
    "x-content-type-options": "Set X-Content-Type-Options to nosniff.",
    "referrer-policy": "Set a Referrer-Policy appropriate for the application.",
}


class WebSecurityService:
    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self._timeout_seconds = timeout_seconds

    def evaluate(
        self,
        domain: str,
    ) -> tuple[WebSecurityPosture, TechnologyFingerprint, SourceStatusItem]:
        errors: list[str] = []
        for scheme in ("https", "http"):
            url = f"{scheme}://{domain}/"
            try:
                response = self._request(url)
            except httpx.TimeoutException:
                errors.append(f"{scheme}: timeout")
                continue
            except httpx.HTTPError as exc:
                errors.append(f"{scheme}: {exc.__class__.__name__}")
                continue

            posture = self._posture_from_response(url, response)
            technology = self._technology_from_headers(response.headers)
            return posture, technology, SourceStatusItem(name="web_security", status="completed")

        logger.warning("web_security_lookup_failed", extra={"domain": domain, "source": "web"})
        return (
            WebSecurityPosture(
                findings=["Web security headers could not be retrieved."],
                recommendations=["Retry web header collection later."],
            ),
            TechnologyFingerprint(findings=["Technology headers could not be retrieved."]),
            SourceStatusItem(
                name="web_security",
                status="failed",
                error="; ".join(errors) or "Web security headers could not be retrieved.",
                error_type="timeout"
                if any("timeout" in error for error in errors)
                else "unexpected_error",
            ),
        )

    def _request(self, url: str) -> httpx.Response:
        try:
            response = httpx.head(
                url,
                timeout=self._timeout_seconds,
                follow_redirects=True,
            )
            if response.status_code in {405, 501}:
                raise httpx.HTTPStatusError(
                    "HEAD not allowed", request=response.request, response=response
                )
            return response
        except httpx.HTTPStatusError:
            return httpx.get(
                url,
                timeout=self._timeout_seconds,
                follow_redirects=True,
            )

    @staticmethod
    def _posture_from_response(url: str, response: httpx.Response) -> WebSecurityPosture:
        score = 100
        findings: list[str] = []
        recommendations: list[str] = []
        header_findings: list[SecurityHeaderFinding] = []

        for header, recommendation in SECURITY_HEADERS.items():
            value = response.headers.get(header)
            present = value is not None
            if present:
                findings.append(f"{_display_header(header)} is present.")
            else:
                score -= 15
                findings.append(f"{_display_header(header)} is missing.")
                recommendations.append(recommendation)
            header_findings.append(
                SecurityHeaderFinding(
                    name=_display_header(header),
                    present=present,
                    value=value,
                    recommendation=None if present else recommendation,
                )
            )

        return WebSecurityPosture(
            checked_url=str(response.url or url),
            status_code=response.status_code,
            headers=header_findings,
            score=max(score, 0),
            findings=findings,
            recommendations=recommendations,
        )

    @staticmethod
    def _technology_from_headers(headers: httpx.Headers) -> TechnologyFingerprint:
        server = headers.get("server")
        powered_by = headers.get("x-powered-by")
        cdn_or_security: list[str] = []
        lower_headers = {key.lower(): value for key, value in headers.items()}
        if "cf-ray" in lower_headers or "cloudflare" in (server or "").lower():
            cdn_or_security.append("Cloudflare")
        if "x-amz-cf-id" in lower_headers or "cloudfront" in (server or "").lower():
            cdn_or_security.append("Amazon CloudFront")
        if "x-sucuri-id" in lower_headers:
            cdn_or_security.append("Sucuri")
        if "x-akamai-transformed" in lower_headers or "akamai" in (server or "").lower():
            cdn_or_security.append("Akamai")

        findings = []
        if server:
            findings.append(f"Server header observed: {server}.")
        if powered_by:
            findings.append(f"X-Powered-By header observed: {powered_by}.")
        if cdn_or_security:
            findings.append(f"CDN/security service hints: {', '.join(cdn_or_security)}.")

        return TechnologyFingerprint(
            server=server,
            powered_by=powered_by,
            cdn_or_security=sorted(set(cdn_or_security)),
            findings=findings,
        )


def _display_header(header: str) -> str:
    return "-".join(part.capitalize() for part in header.split("-"))
