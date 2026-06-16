# Project Eye Security Rules

Version: 1.0

Applies To: Contributors, maintainers, AI coding agents, and reviewers.

---

## Secure Coding Expectations

All code must:

- Validate user-controlled input.
- Return safe structured errors.
- Avoid exposing stack traces in API responses.
- Use explicit dependency boundaries.
- Avoid offensive automation.
- Respect passive-only Domain Intelligence scope.

Security controls must be added intentionally and documented.

---

## Secret Handling Rules

Never:

- Commit secrets.
- Hardcode API keys.
- Hardcode credentials.
- Store tokens in frontend code.
- Log secrets.
- Include secrets in examples.

Always:

- Use environment variables.
- Keep `.env` files out of version control.
- Use `.env.example` for non-secret configuration examples.
- Rotate any exposed secret.

---

## Logging Restrictions

Logs may include:

- Request ID.
- Endpoint.
- Status code.
- Duration.
- Safe validation failure reason.
- Safe dependency failure reason.

Logs must not include:

- API keys.
- Tokens.
- Passwords.
- Credentials.
- Raw secrets.
- Sensitive environment values.
- Full unreviewed external payloads.

Logging must help operations without leaking sensitive data.

---

## Third-Party Dependency Rules

Dependencies must be:

- Necessary.
- Actively maintained.
- Compatible with the project stack.
- Locked or pinned through project tooling.
- Reviewed for security risk.

Before adding a dependency:

- Check whether the standard library or existing stack already solves the need.
- Review package purpose and maintenance status.
- Run dependency vulnerability checks when tooling exists.
- Avoid packages with unnecessary privileges.

---

## Security Review Process

Security review is required when changes affect:

- Input validation.
- External source access.
- Identity or access controls if a future roadmap explicitly promotes them into scope.
- Secrets handling.
- Logging.
- Database persistence.
- Dependency versions.
- Deployment configuration.

Review steps:

1. Confirm the change is in scope.
2. Confirm prohibited use cases remain excluded.
3. Confirm secrets are not exposed.
4. Confirm validation and error handling are documented.
5. Confirm logs are safe.
6. Confirm dependency risk was reviewed.
