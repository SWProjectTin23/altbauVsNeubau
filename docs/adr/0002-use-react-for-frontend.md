# Use React for Frontend

Date: 2025-07-15

## Status

Accepted

## Context

We need to build an interactive and responsive web interface that displays sensor data (e.g., air quality, temperature, humidity) and provides a user-friendly experience for exploring and comparing time-series data. The frontend must be modular, easy to maintain, and capable of integrating with REST APIs provided by the backend.

The team already has solid experience with React, and we value a fast development cycle, reusable components, and a large ecosystem of community tools and libraries.

### Alternatives Considered

We considered several frontend options:

- Vanilla JS / HTML / CSS — too low-level and inefficient for building a scalable UI.
- Vue.js — simpler than React but unfamiliar to most team members.
- Angular — powerful, but has a steep learning curve and introduces more complexity than needed.
- React — balances flexibility and structure, and is already well known by the team.

## Decision

We will use React as the frontend framework.

React enables us to:

- Build reusable, component-based UIs efficiently.
- Leverage existing team expertise to accelerate development.
- Integrate third-party libraries (e.g., charts, maps) easily.
- Maintain flexibility in how we structure and scale the frontend.

## Consequences

- We can start quickly without a steep learning curve.
- Our stack will require additional decisions (e.g., state management, routing), which we will document in separate ADRs.
- Build and deployment will be handled via Docker and integrated into our docker-compose setup.