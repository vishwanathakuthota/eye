# Project Eye Architecture Rules

Version: 1.0

Applies To: Architecture decisions, implementation planning, and AI coding agents.

---

## Architecture Principles

Project Eye architecture must optimize for:

- Clarity.
- Maintainability.
- Local validation.
- Explicit boundaries.
- Small, reviewable increments.

Architecture decisions must be grounded in the PRD and current sprint scope.

---

## Simplicity First

Prefer the smallest design that satisfies the current sprint.

Allowed v0.1 components:

- Next.js
- FastAPI
- PostgreSQL
- Docker Compose

Do not introduce extra infrastructure to prepare for future milestones.

---

## No Over-Engineering

Avoid:

- Microservices.
- Hidden abstraction layers.
- Premature plugin systems.
- Background workers unless explicitly in scope.
- Search or graph infrastructure unless explicitly in scope.
- Production orchestration before local validation is complete.

Do not add complexity because it may be useful later.

---

## Current Sprint Boundaries

Before designing or generating code:

1. Read the required project documents.
2. Identify the current sprint.
3. Confirm the allowed scope.
4. Implement only that scope.

When the current sprint is documentation-only, do not create backend code, frontend code, Docker files, migrations, or application services.

---

## Future Roadmap Constraints

The following may appear only as future roadmap placeholders unless explicitly promoted into the current sprint:

- Neo4j
- OpenSearch
- Celery
- Redis
- Kubernetes
- Authentication
- Billing
- AI agents
- Microservices

Future placeholders must not become required v0.1 components by implication.

---

## Architecture Review Checklist

Before accepting an architecture change:

- Does it match the PRD?
- Does it match the current sprint?
- Does it preserve v0.1 Domain Intelligence scope?
- Does it avoid prohibited components?
- Does it keep service boundaries explicit?
- Does it keep local development simple?
- Does documentation reflect the decision?
