# Eye

Search Anything. Understand Everything.

Eye is an AI-native intelligence search engine. The current repository state is Sprint 002: the v0.1 Domain Intelligence engine.

This sprint includes:

- FastAPI backend with `GET /api/v1/health`
- Domain Intelligence endpoint at `GET /api/v1/domain?domain=<domain>`
- Domain validation
- DNS lookup
- RDAP lookup
- crt.sh certificate transparency lookup
- Risk scoring
- Intelligence summary generation
- PostgreSQL persistence
- Next.js TypeScript frontend landing page
- Unit and API tests

IP Intelligence, Threat Intelligence, authentication, Reports UI, Redis, Celery, Neo4j, OpenSearch, and AI agents are intentionally not implemented in Sprint 002.

## Requirements

- Python 3.12+
- Node.js 22.13+
- Docker and Docker Compose

## Environment

Create a local environment file from the example:

```bash
cp .env.example .env
```

The example values are for local development only.

## Backend

Install backend dependencies:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the backend:

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/api/v1/health
```

Analyze a domain:

```bash
curl "http://localhost:8000/api/v1/domain?domain=example.com"
```

## Frontend

Install frontend dependencies:

```bash
cd frontend
npm ci
```

Run the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## Docker Compose

Run the local stack:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/api/v1/health`
- PostgreSQL: `localhost:5432`

Validate Compose configuration:

```bash
docker compose config
```

## Tests

Run backend tests:

```bash
python3 -m pytest tests/backend
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Sprint 002 Scope

Allowed:

- Domain Search Endpoint
- Domain Validation
- DNS Lookup Service
- RDAP Lookup Service
- crt.sh Integration
- Risk Scoring Engine
- Intelligence Summary Generator
- PostgreSQL Persistence
- Unit Tests
- API Tests

Not allowed:

- IP Intelligence
- Threat Intelligence
- Reports UI
- Authentication
- Redis, Celery, Neo4j, OpenSearch, Kubernetes, or AI agents
