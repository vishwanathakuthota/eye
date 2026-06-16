from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

DOMAIN_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


class DomainValidationError(ValueError):
    pass


class DomainValidator:
    def validate(self, value: str | None) -> str:
        if value is None or not value.strip():
            raise DomainValidationError("Domain is required.")

        candidate = value.strip().lower().rstrip(".")

        parsed = urlsplit(candidate)
        if parsed.scheme or parsed.netloc or any(char in candidate for char in "/?#@"):
            raise DomainValidationError("Domain must be a hostname, not a URL.")

        if (
            candidate == "localhost"
            or candidate.endswith(".localhost")
            or candidate.endswith(".local")
        ):
            raise DomainValidationError("Localhost and local network names are not supported.")

        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            pass
        else:
            raise DomainValidationError("IP addresses are not supported for Domain Intelligence.")

        if "*" in candidate or any(char.isspace() for char in candidate):
            raise DomainValidationError("Domain contains unsupported characters.")

        if len(candidate) > 253 or "." not in candidate:
            raise DomainValidationError("Domain must contain at least one valid DNS suffix.")

        try:
            ascii_domain = candidate.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise DomainValidationError("Domain cannot be normalized.") from exc

        labels = ascii_domain.split(".")
        if any(not label or len(label) > 63 for label in labels):
            raise DomainValidationError("Domain label length is invalid.")

        if any(DOMAIN_LABEL_PATTERN.fullmatch(label) is None for label in labels):
            raise DomainValidationError("Domain contains invalid DNS label characters.")

        return ascii_domain
