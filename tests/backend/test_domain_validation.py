from __future__ import annotations

import pytest

from app.services.domain_validation import DomainValidationError, DomainValidator


def test_domain_validator_normalizes_valid_domain() -> None:
    validator = DomainValidator()

    assert validator.validate(" Example.COM. ") == "example.com"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://example.com",
        "example.com/path",
        "127.0.0.1",
        "localhost",
        "*.example.com",
        "user@example.com",
    ],
)
def test_domain_validator_rejects_unsupported_input(value: str) -> None:
    validator = DomainValidator()

    with pytest.raises(DomainValidationError):
        validator.validate(value)
