# Eye

Search Anything. Understand Everything.

Eye is an AI-native intelligence search engine. The current repository state is Sprint 001: a local development foundation for the v0.1 Domain Intelligence alpha.

This sprint includes only the repository skeleton:

- FastAPI backend with `GET /api/v1/health`
- Next.js TypeScript frontend landing page
- PostgreSQL local service through Docker Compose
- Environment configuration example
- Minimal backend health test

Domain Intelligence, RDAP, DNS, crt.sh, reports, authentication, Redis, Celery, Neo4j, OpenSearch, and AI agents are intentionally not implemented in Sprint 001.

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/api/v1/health
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

## Sprint 001 Scope

Allowed:

- Backend skeleton
- Frontend skeleton
- Docker Compose local stack
- Environment configuration
- Health endpoint
- Landing page
- Basic local run documentation

Not allowed:

- Domain Intelligence logic
- DNS lookup
- RDAP lookup
- crt.sh integration
- Report generation or retrieval implementation
- Authentication
- Threat intelligence connectors
- Redis, Celery, Neo4j, OpenSearch, Kubernetes, or AI agents
