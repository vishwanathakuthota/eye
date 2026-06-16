PROJECT_RULES.md

Eye Project Rules

Version: 1.0

Applies To:
All contributors, AI coding agents, Codex sessions, and future maintainers.

⸻

Mission

Eye is an AI-Native Intelligence Search Engine.

Its purpose is to transform publicly available information into actionable intelligence.

Eye is not an offensive security platform.

Eye is not a scanning tool.

Eye is not an exploitation framework.

Every feature must align with the mission:

Search Anything.
Understand Everything.

⸻

Development Philosophy

Follow:

Documentation First

Architecture First

Code Second

Never generate code before understanding:

* PRD.md
* Architecture
* Current Sprint
* Open Issues

⸻

Scope Control

Implement only what is requested.

Do not anticipate future features.

Do not build speculative functionality.

Do not create hidden abstractions for future milestones.

Build only for the current sprint.

⸻

Repository Structure

Maintain:

backend/

frontend/

docs/

tests/

.github/

.codex/

No ad-hoc directories.

No experimental folders.

No temporary files committed.

⸻

Backend Standards

Language:

Python

Framework:

FastAPI

Requirements:

* Type hints required
* Pydantic validation required
* Structured logging required
* Dependency injection preferred
* API versioning mandatory

API format:

/api/v1

⸻

Frontend Standards

Framework:

Next.js

Language:

TypeScript

Requirements:

* Strict typing enabled
* Reusable components
* Responsive design
* No inline business logic

⸻

Database Standards

Database:

PostgreSQL

ORM:

SQLAlchemy

Migration Tool:

Alembic

Requirements:

* All schema changes via migrations
* No direct schema modifications
* Soft delete preferred when applicable

⸻

Security Standards

Never:

* Store secrets in source code
* Commit credentials
* Hardcode tokens
* Disable validation

Always:

* Use environment variables
* Validate inputs
* Sanitize outputs
* Log security-relevant events

⸻

Logging Standards

Use structured logging.

Every service should log:

* Request start
* Request end
* Errors
* External API failures

Never log:

* Secrets
* API keys
* Credentials

⸻

Testing Standards

Every feature should include:

* Unit tests
* Service tests

Target:

Minimum 80% coverage.

⸻

Documentation Standards

Every major feature must update:

README.md

Relevant docs/

API documentation

Architecture documentation

⸻

Coding Standards

Prefer:

Readable code

Simple code

Explicit code

Avoid:

Premature optimization

Over-engineering

Deep inheritance trees

Magic behavior

⸻

Git Standards

Branch Naming

feature/

fix/

docs/

refactor/

Example:

feature/domain-intelligence

⸻

Commit Standards

Format:

type: description

Examples:

feat: add RDAP service

fix: correct DNS parsing

docs: update architecture diagram

refactor: simplify risk engine

⸻

Pull Request Standards

Every PR must:

* Pass tests
* Pass linting
* Update documentation
* Include meaningful description

⸻

AI Agent Instructions

Before generating code:

1. Read PRD.md
2. Read PROJECT_RULES.md
3. Identify current sprint
4. Implement only requested scope

Never:

* Invent requirements
* Invent features
* Invent APIs
* Invent milestones

When uncertain:

Ask for clarification.

⸻

Release Strategy

Development

↓

Local Validation

↓

Docker Validation

↓

Internal Alpha

↓

Private Beta

↓

Production Release

↓

eye.openvalidations.com

⸻

Final Principle

Eye prioritizes:

Clarity over complexity.

Maintainability over cleverness.

Intelligence over data.

Quality over speed.