# No Authentication for the Web Application

**Date:** 2025-07-24  
**Status:** Accepted

## Context

The web frontend is designed to display environmental sensor data such as temperature, humidity, pollen levels, and particulate matter. While the application allows basic user interactions—like setting local threshold alerts and selecting time ranges—it does not involve any sensitive, personal, or private data.

There are no user-specific features that require persistent identity, and no operations that could compromise the system or data integrity. The main functionality is read-only access to public environmental data.

Implementing authentication would require significant effort (backend logic, token management, secure storage, error handling) without a clear benefit to the user or system.

## Alternatives Considered

- **Implement authentication via OAuth or custom login system** – Secure, but adds complexity, infrastructure overhead, and unnecessary friction for the user.
- **Anonymous access with optional settings stored locally** – Simple, fast, and meets current functional needs.

## Decision

We will **not implement any authentication mechanism** in the frontend application at this stage.

All data access will remain anonymous and unrestricted. Local settings (e.g., custom thresholds or selected views) will be stored in the database.

## Consequences

- **Simplified development** – No need for user account handling, token management, session expiration, or login UI.
- **Faster user access** – Users can access the application instantly without sign-in barriers.
- **Limited personalization** – Only basic preferences are supported.
- **Potential future requirement** – If more advanced user-specific functionality (e.g., saving settings to a backend, sharing views) is introduced, authentication may need to be revisited in a future ADR.

