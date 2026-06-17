from __future__ import annotations

import ipaddress
from ipaddress import IPv4Address, IPv6Address


class IpValidationError(ValueError):
    pass


class IpValidator:
    def validate(self, value: str | None) -> IPv4Address | IPv6Address:
        if value is None or not value.strip():
            raise IpValidationError("IP address is required.")

        candidate = value.strip()
        if any(character.isspace() for character in candidate):
            raise IpValidationError("IP address must not contain whitespace.")

        try:
            return ipaddress.ip_address(candidate)
        except ValueError as exc:
            raise IpValidationError("IP address must be a valid IPv4 or IPv6 address.") from exc
