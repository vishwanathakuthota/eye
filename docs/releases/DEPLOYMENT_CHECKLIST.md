# Project Eye Deployment Checklist

Version: v0.1.0-alpha

Stage: Phase 0 - Repository Foundation

Scope: Local development validation

---

## Purpose

This checklist defines the minimum validation gates before code is committed, pushed, or considered ready for a local alpha release.

Project Eye v0.1 is limited to Domain Intelligence and local development. This checklist must not be used to approve production deployment.

---

## Pre-Commit Checks

Before committing:

- Confirm the change matches the current sprint scope.
- Confirm no backend, frontend, Docker, or infrastructure code was changed during documentation-only phases.
- Confirm no secrets were added.
- Confirm `.env` files are not staged.
- Confirm generated cache files are not staged.
- Confirm documentation links and file paths are accurate.
- Confirm Markdown headings are readable in GitHub.
- Confirm non-goals remain intact.

Recommended commands:

```bash
git status --short
git diff --check
```

---

## Pre-Push Checks

Before pushing:

- Re-read changed documentation.
- Review `git diff --cached`.
- Confirm commit messages follow project rules.
- Confirm no unrelated changes are staged.
- Confirm no generated artifacts are staged.
- Confirm no secret-like values appear in staged content.

Recommended commands:

```bash
git diff --cached --check
git status --short
```

---

## Local Deployment Checks

For local development validation:

- Confirm required environment variables are documented in `.env.example`.
- Confirm FastAPI starts locally when backend work is in scope.
- Confirm Next.js starts locally when frontend work is in scope.
- Confirm PostgreSQL connection settings are local-development safe.
- Confirm the health endpoint returns the standard success shape.

Health endpoint validation:

```bash
curl http://localhost:8000/api/v1/health
```

---

## Docker Validation

When Docker changes are in scope:

- Confirm `docker compose config` passes.
- Confirm Docker Compose uses only allowed v0.1 components.
- Confirm services do not require undeclared secrets.
- Confirm PostgreSQL has a local volume.
- Confirm backend and frontend ports are explicit.
- Confirm service health checks are configured where applicable.

Recommended command:

```bash
docker compose config
```

---

## Security Validation

Before release validation:

- Confirm no secrets are committed.
- Confirm logs do not expose secrets.
- Confirm error examples do not expose stack traces.
- Confirm input validation requirements are documented.
- Confirm dependency checks have been run when dependencies changed.
- Confirm prohibited use cases remain excluded.
- Confirm external source usage remains passive.

Recommended checks:

```bash
git diff --cached
```

---

## Release Validation

Before tagging or announcing a release:

- Confirm the release scope matches the version strategy.
- Confirm documentation is current.
- Confirm API documentation matches implemented endpoints.
- Confirm architecture documentation matches implemented components.
- Confirm security documentation matches implemented controls.
- Confirm local deployment validation passed.
- Confirm rollback expectations are documented.
- Confirm changelog or release notes are prepared.

Phase 0 release validation requires documentation completeness, not production readiness.
