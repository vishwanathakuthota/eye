# Project Eye Git Workflow

Version: 1.0

Applies To: Contributors, maintainers, AI coding agents, and release operators.

---

## Principles

Project Eye uses a pull-request-first workflow. Work should be scoped, reviewable, and aligned to the current sprint.

Do not push directly to `main`.

---

## Branch Naming

Use one of the approved branch prefixes:

- `feature/<short-name>`
- `fix/<short-name>`
- `bug/<short-name>`
- `release/<version>`
- `docs/<short-name>`

Examples:

```text
feature/domain-validation
fix/health-response-shape
bug/docker-build
release/v0.1.0-alpha
docs/api-spec
```

Keep branch names lowercase and descriptive. Use hyphens between words.

---

## Commit Style

Use short, explicit commit messages:

- `feat:`
- `fix:`
- `bug:`
- `docs:`
- `test:`
- `chore:`
- `refactor:`
- `security:`
- `release:`

Examples:

```text
feat: add domain validation service
fix: correct health response metadata
bug: handle empty crtsh response
docs: update API examples
test: add domain endpoint coverage
chore: add GitHub workflow discipline
refactor: simplify risk scoring
security: redact external source errors
release: prepare v0.1.0-alpha
```

Commits should be focused. Do not mix unrelated changes.

---

## Pull Request Rules

- No direct push to `main`.
- Every feature requires a pull request.
- Every bugfix requires a pull request.
- Every release requires a pull request.
- All checks must pass before merge.
- Documentation must be updated when behavior changes.
- Security impact must be reviewed before merge.
- Deployment notes are required for migrations, environment changes, or operational changes.

---

## Required Checks

CI must validate:

- Backend dependency installation.
- Backend linting with Ruff.
- Backend formatting with Ruff.
- Backend tests with Pytest.
- Python compilation with `compileall`.
- Frontend dependency installation.
- Frontend linting.
- Frontend build.
- Frontend dependency audit.
- Docker Compose configuration.
- Docker Compose build.

Security workflow must validate:

- Frontend dependency audit.
- Python dependency audit.
- Secret scanning.

---

## Review Expectations

Reviewers should confirm:

- The change matches the current sprint.
- No prohibited components are introduced.
- Domain Intelligence remains passive.
- Secrets are not committed.
- Logs do not expose sensitive values.
- API changes match `docs/api/API_SPEC.md`.
- Architecture changes match `docs/architecture/ARCHITECTURE.md`.
- Tests cover changed behavior.

---

## Release Branches

Release branches use:

```text
release/<version>
```

Release pull requests must include:

- Version.
- Scope.
- Validation evidence.
- Changelog notes.
- Deployment notes.
- Rollback plan.

---

## Emergency Fixes

Emergency fixes still require a pull request.

Use:

```text
fix/<short-name>
```

or:

```text
bug/<short-name>
```

Keep the change minimal, document the risk, and run all relevant checks before merge.
