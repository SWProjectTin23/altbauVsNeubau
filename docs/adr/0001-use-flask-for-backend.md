# Use Flask for backend

Date: 2025-07-15

## Status

Accepted

## Context

We need to implement a lightweight, maintainable backend service that exposes APIs to receive sensor data (e.g. from MQTT), store them in a database, and provide endpoints for the frontend to retrieve data and system states. The team is familiar with Python, and many sensor and scientific data tools integrate well with the Python ecosystem. Therefore, a Python-based web framework is preferred.

### Alternatives Considered

We are choosing between popular Python frameworks like Flask, FastAPI, and Django. While Django provides many features out of the box, it may be too heavy for our use case. FastAPI offers async features and automatic docs, but the team has more experience with Flask and prefers its simplicity for this project’s initial scope.

## Decision

We will use **Flask** as the backend framework.

Flask allows us to:
- Build REST APIs quickly with minimal boilerplate.
- Keep the project structure lean and focused.
- Easily integrate with libraries for MQTT and PostgreSQL.

## Consequences
- The backend will be synchronous by default, which is acceptable for our current scale.
- If performance becomes an issue, we may revisit the choice or offload heavy processing to background tasks.
- We will write modular Flask blueprints to maintain clarity and allow future refactoring.
