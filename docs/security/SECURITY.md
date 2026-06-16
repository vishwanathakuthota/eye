# Project Eye Security

Version: v0.1.0-alpha

Stage: Phase 0 - Repository Foundation

Scope: Local development and passive Domain Intelligence

---

## Security Position

Project Eye transforms publicly available information into actionable intelligence.

Eye is not an offensive security platform, scanning tool, exploitation framework, malware execution environment, credential collection system, or social engineering platform.

The v0.1 security posture assumes local development, passive public data collection, explicit input validation, conservative logging, and responsible source usage.

---

## Responsible Use Policy

Project Eye may be used for:

- Defensive security research.
- Domain ownership and infrastructure review.
- Passive public intelligence aggregation.
- Internal analyst workflow validation.
- Risk assessment using lawful public sources.
- Educational and research workflows that respect applicable rules.

Users and maintainers are responsible for following applicable laws, source terms, organizational policies, and authorization requirements.

---

## Prohibited Use Cases

Project Eye must not be used for:

- Active scanning without authorization.
- Exploitation.
- Credential theft or credential collection.
- Malware execution, delivery, or analysis automation.
- Social engineering.
- Harassment, stalking, doxxing, or targeting private individuals.
- Circumventing access controls.
- Evading rate limits or source restrictions.
- Dark web monitoring in v0.1.
- Offensive automation.

Features that enable prohibited use must not be added.

---

## Input Validation

All user-controlled input must be validated before processing.

Domain inputs must:

- Be required.
- Be trimmed and normalized.
- Be validated as hostnames.
- Reject URLs, paths, query strings, and fragments.
- Reject IP addresses, localhost, and private network targets.
- Reject shell syntax, scripts, wildcards, and email addresses.
- Enforce DNS length limits.

Validation failures must:

- Return standard API error responses.
- Avoid external calls.
- Avoid persistence side effects.
- Produce safe structured logs.

---

## Secrets Management

Secrets must never be committed to source control.

Rules:

- Use environment variables for secrets.
- Keep local environment files out of version control.
- Never hardcode API keys, tokens, passwords, or credentials.
- Never expose secrets in frontend code.
- Never print secrets in logs, test output, error responses, or documentation examples.
- Rotate any secret that is accidentally exposed.

v0.1 should prefer public unauthenticated sources where practical. Any authenticated source integration must follow these rules.

---

## Logging Standards

Project Eye must use structured logging when backend code is introduced or changed.

Log:

- Request start.
- Request completion.
- Request ID.
- Endpoint.
- Status code.
- Duration.
- Validation failures.
- External source failures.
- Database errors.

Do not log:

- API keys.
- Tokens.
- Passwords.
- Credentials.
- Raw secrets.
- Sensitive environment values.
- Full external payloads unless explicitly reviewed.
- Personal data beyond what is necessary for safe debugging.

Logs must help diagnose behavior without exposing sensitive data.

---

## Dependency Management

Dependency choices must be conservative.

Rules:

- Keep dependencies minimal.
- Prefer actively maintained packages.
- Pin or lock versions through project tooling.
- Review package purpose before adding it.
- Avoid packages that require unnecessary network, filesystem, or process privileges.
- Remove unused dependencies.
- Run dependency vulnerability checks before release.

Security updates affecting API handling, parsing, HTTP clients, database access, build tooling, or framework runtime must be prioritized.

---

## Rate Limiting Strategy

Rate limiting protects both Project Eye and external public sources.

v0.1 rate limiting expectations:

- Apply conservative local request limits before public or shared deployment.
- Limit repeated failed validation attempts.
- Prevent accidental loops against passive external sources.
- Return `429 Too Many Requests` with the standard error shape.
- Make rate limits configurable through environment configuration when implemented.

Phase 0 documents the strategy. Implementation belongs to a future sprint unless explicitly requested.

---

## External API Handling

External source usage must be passive and respectful.

Rules:

- Respect source terms and rate limits.
- Use timeouts for external requests.
- Handle failed, partial, malformed, and empty responses.
- Represent source status in reports.
- Avoid retry storms.
- Do not scrape in ways that violate source rules.
- Do not treat missing data as proof of safety.

External integrations are not implemented in Phase 0.

---

## Responsible Disclosure Process

Security issues should be reported privately to the project owner before public disclosure.

Reports should include:

- Summary of the issue.
- Impact.
- Affected version or commit.
- Reproduction steps.
- Suggested mitigation if known.

Reports should not include live secrets, third-party private data, or unsafe exploit payloads beyond what is necessary to demonstrate impact responsibly.

---

## Local Development Security Baseline

For local development:

- Run services only on local development interfaces unless explicitly needed.
- Do not expose local services directly to the public internet.
- Keep `.env` files out of version control.
- Use local-only test data.
- Validate all API input.
- Use structured error responses.
- Avoid stack traces in API responses.
- Review logs before sharing them.
- Keep reports limited to passive public intelligence.
