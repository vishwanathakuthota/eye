from __future__ import annotations

import pytest

from app.services.ip_validation import IpValidationError, IpValidator


def test_ip_validator_normalizes_ipv4() -> None:
    result = IpValidator().validate("  8.8.8.8  ")

    assert str(result) == "8.8.8.8"
    assert result.version == 4


def test_ip_validator_normalizes_ipv6() -> None:
    result = IpValidator().validate("2001:4860:4860::8888")

    assert str(result) == "2001:4860:4860::8888"
    assert result.version == 6


@pytest.mark.parametrize(
    "value",
    [
        "",
        "example.com",
        "999.999.999.999",
        "8.8.8.8/32",
        "8.8.8.8 value",
    ],
)
def test_ip_validator_rejects_invalid_input(value: str) -> None:
    with pytest.raises(IpValidationError):
        IpValidator().validate(value)
