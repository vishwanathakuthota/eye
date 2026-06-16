# Project Eye Architecture

Version: v0.1.0-alpha

Stage: Phase 0 - Repository Foundation

Scope: Domain Intelligence only

---

## System Overview

Project Eye is an AI-native intelligence search engine for transforming publicly available information into actionable intelligence.

The v0.1 product scope is limited to Domain Intelligence. The architecture must stay small, local-first, and easy to reason about while the repository foundation, API contracts, security posture, and release discipline are established.

The only required v0.1 platform components are:

- Next.js
- FastAPI
- PostgreSQL
- Docker Compose

No other infrastructure component is required for v0.1.

---

## High-Level Architecture

```text
User
  |
  v
Next.js Frontend
  |
  v
FastAPI Backend (/api/v1)
  |
  +--> Domain validation boundary
  +--> Domain intelligence orchestration boundary
  +--> Report assembly boundary
  |
  v
PostgreSQL
```

External public sources are accessed only through backend service boundaries once Domain Intelligence implementation begins. Phase 0 defines the shape of the system; it does not implement intelligence collection.

---

## Component Responsibilities

### Next.js Frontend

The frontend provides the local analyst interface.

Responsibilities:

- Render the user-facing application shell.
- Collect domain search input once Domain Intelligence work begins.
- Call backend APIs under `/api/v1`.
- Display loading, success, empty, and error states.
- Present domain findings, reports, summaries, and risk information after those features are implemented.

The frontend must not:

- Call external intelligence sources directly.
- Access PostgreSQL directly.
- Store secrets.
- Implement risk scoring or intelligence logic.

### FastAPI Backend

The backend owns API contracts, validation, orchestration, and persistence boundaries.

Responsibilities:

- Expose versioned REST APIs under `/api/v1`.
- Provide `GET /api/v1/health`.
- Validate request input before any processing.
- Coordinate future Domain Intelligence service boundaries.
- Persist reports to PostgreSQL when report implementation begins.
- Return standard success and error response shapes.
- Apply structured logging and secure error handling.

The backend must not:

- Implement active scanning.
- Implement exploitation or offensive automation.
- Introduce authentication in v0.1.
- Introduce billing in v0.1.
- Introduce microservices in v0.1.

### PostgreSQL

PostgreSQL is the v0.1 system of record.

Responsibilities:

- Store future domain analysis records.
- Store normalized findings once implemented.
- Store report metadata and retrieval identifiers.
- Support local development validation.

PostgreSQL is accessed only from backend persistence boundaries.

### Docker Compose

Docker Compose is the local development orchestration layer.

Responsibilities:

- Run the frontend, backend, and PostgreSQL locally.
- Provide repeatable local validation.
- Support repository foundation and alpha testing.

Docker Compose is not a production orchestration strategy.

---

## Data Flow

### Phase 0 Foundation Flow

```text
Developer
  |
  v
Docker Compose
  |
  +--> FastAPI health endpoint
  +--> Next.js application shell
  +--> PostgreSQL local service
```

Phase 0 validates that the repository can run locally and expose a health endpoint.

### v0.1 Domain Intelligence Flow

```text
User submits domain
  |
  v
Next.js sends request to FastAPI
  |
  v
FastAPI validates domain
  |
  v
Backend service boundaries query passive public sources
  |
  v
Backend normalizes findings and assembles report
  |
  v
Backend stores report in PostgreSQL
  |
  v
Frontend displays report
```

This v0.1 flow is a target architecture. Phase 0 does not implement the intelligence steps.

---

## Service Boundaries

Eye v0.1 is a modular monolith, not a microservices system.

Required boundaries:

- API boundary: versioned REST endpoints under `/api/v1`.
- Validation boundary: request validation before external calls or persistence.
- Domain Intelligence boundary: future passive collection and normalization.
- Report boundary: future report assembly and retrieval.
- Persistence boundary: PostgreSQL access through backend code only.

Boundaries are code organization and ownership boundaries. They are not separate deployable services in v0.1.

---

## External Integrations

v0.1 Domain Intelligence may later use passive public sources such as:

- DNS resolvers.
- RDAP services.
- Certificate transparency sources such as crt.sh.

Rules:

- External integrations must be passive.
- External calls must originate from backend service boundaries only.
- Source terms and rate limits must be respected.
- Failures must be isolated and represented in report source status.
- Secrets and tokens must never be logged.

Phase 0 does not implement external integrations.

---

## Database Responsibilities

PostgreSQL will support future v0.1 report persistence.

Expected data responsibilities:

- Domain analysis request metadata.
- Normalized DNS findings.
- Normalized RDAP findings.
- Certificate transparency findings.
- Discovered subdomains.
- Risk score and risk level.
- Report summary and report retrieval metadata.

Database rules:

- All schema changes must be managed through migrations once schema work begins.
- Direct manual schema edits are not allowed.
- Application code must own database access through explicit persistence boundaries.
- Secrets must not be stored in report records.

---

## Future Architecture Considerations

The following may be considered after v0.1 validation:

- Additional threat intelligence connectors.
- Historical report comparison.
- Organization, IP, and indicator intelligence.
- Search indexing.
- Graph intelligence storage.
- Background processing.
- Authentication and authorization.
- Production orchestration.
- Agent-assisted workflows.

These are future roadmap placeholders only. They are not v0.1 requirements.

---

## Non-Goals

The following are not part of Phase 0 or required v0.1 architecture:

- Neo4j
- OpenSearch
- Celery
- Redis
- Kubernetes
- Authentication
- Billing
- AI agents
- Microservices
- Active scanning
- Exploitation modules
- Malware execution
- Credential collection
- Social engineering capabilities
- Dark web monitoring
