# Logging Guidelines (Foundational)

## Purpose
Provide uniform, minimal, high-signal logging supporting diagnostics, observability, and incident analysis without leaking sensitive data.

## Scope
Applies to backend API, database interaction layer, MQTT ingestion, and auxiliary services. Complements the exception hierarchy defined in `backend/exceptions.py`.

## Core Principles
- Consistency over individuality.
- Signal over volume (each log line must justify its existence).
- Single source of truth per failure (no duplicate logging of identical error states).
- Separation of concerns: logging records state; exception types convey semantics.
- No sensitive data (credentials, raw tokens, PHI) in log content.

## Severity Semantics
- DEBUG: Transient diagnostic detail; safe to disable in production.
- INFO: Lifecycle milestones and stable operational state changes.
- WARNING: Recoverable anomalies; degraded but functioning.
- ERROR: Failed operation requiring attention; user request not fulfilled.
- CRITICAL: System integrity or availability compromised.

## Exception Alignment
- ValidationError / NotFoundError: WARNING level.
- DatabaseError, DatabaseConnectionError, DatabaseTimeoutError: ERROR level.
- MQTTError, MQTTConnectionError, MQTTTimeoutError: ERROR level.
- Unexpected / uncategorized (AppError fallback): ERROR or escalated as CRITICAL if systemic.

## Content Standards
Each entry should answer: WHAT happened, CONTEXT (entity / subsystem), OUTCOME (success/failure), and optionally CORRELATION (request/device identifiers). Avoid HOW (stack traces) except at controlled boundaries.

## Structure
- Timestamp, level, logger name, concise message.
- Optional correlation identifiers (request id, device id, message id).
- Stable key ordering to facilitate parsing and search.

## Correlation & Traceability
Introduce and propagate lightweight correlation identifiers across request, DB, and MQTT boundaries to link related events without inflating message size.

## Performance Considerations
- Avoid expensive string construction unless the level is enabled.
- Limit high-frequency logging (loop iterations, per message noise).
- Prefer aggregating counts or rates externally (metrics) rather than logging repetitive granular events.

## Life Cycle Coverage
Log only at meaningful transition points:
- Start / completion of external boundary interactions (API request accepted / responded).
- Resource acquisition failures (DB connect, broker connect).
- State transitions (service ready, graceful shutdown).
- Timeouts and retries (first occurrence, final failure).

## De-Duplication
Do not log inside deeply nested helpers if the caller already logs the failure context. Adopt a “log at boundary” policy: business logic raises typed exceptions; outer layer logs once if not already auto-logged by construction.

## Privacy & Compliance
Validate that no log line contains secrets, raw queries with embedded credentials, or personally identifiable sensor metadata beyond necessary identifiers.

## Evolution
Changes to format, levels, or correlation strategy require:
1. Justification (observed deficiency).
2. Agreement within the team.
3. Update of this guideline.
4. Backward awareness (impact on log parsers / dashboards).

## Anti-Patterns
- Logging and rethrowing unchanged repeatedly.
- Embedding control flow decisions on log text content.
- Excessive DEBUG left enabled in production causing noise.
- Mixing user-facing phrasing with internal operational messages.

## Success Criteria
- Operators can trace an error path end-to-end with minimal lines.
- No sensitive data discovered during routine audits.
- Log volume remains proportionate to traffic growth.
- Distinct exception classes map predictably to severity.

---

## Frontend Extension (Browser Runtime)

### Goals
- Preserve parity with backend diagnostics (correlation).
- Minimize noise in production builds.
- Enable opt‑in verbose diagnostics (feature flags / log level variable).

### Log Channels
| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| Network Wrapper | Structured console output (guarded) | Request lifecycle & failures |
| Error Boundary | console.error | Render-time crashes |
| Domain Modules | console.debug/info | Conditional diagnostic detail |
| Performance | Performance API + optional summary log | Latency instrumentation |

### Levels Mapping
| Console | Semantics Alignment |
|---------|---------------------|
| console.debug | Detailed dev-only traces (requires LOG_LEVEL=debug) |
| console.info | High-level lifecycle events (data loaded, cache miss) |
| console.warn | Recoverable client anomalies (deprecated API usage, stale data) |
| console.error | Unhandled exceptions, irrecoverable failures |

### Activation Control
- Use env variable `VITE_LOG_LEVEL` (e.g. `silent`, `error`, `warn`, `info`, `debug`).
- Wrapper decides if a given level emits.
- Default production build: `warn`.

### Structured Wrapper
Create a lightweight logger that prefixes subsystem + correlation id (if available). Do not use raw `console.*` directly in feature code.

### Correlation
- Accept optional `corrId` propagated from backend response headers or generated in session.
- Include `corrId` consistently for request + error log pairs to support cross-layer triage.

### Error Logging Policy
- Errors surfaced to UI should have exactly one corresponding `console.error`.
- Exceptions translated to friendly messages (ValidationError, etc.) may be logged at `info` unless unexpected.

### Network Logging
- Log request start (debug) only when correlation/tracing required.
- Always log failures (error) with endpoint + summarized classification (e.g. `NetworkError`, `TimeoutError`, `ValidationError`).
- Exclude full payloads unless sanitized & level=debug.

### Sensitive Data
Never log:
- Authentication tokens
- Raw sensor payloads containing personally identifiable metadata
- Full backend error stack text (backend already retains)

### Redaction
If partial payload context required (debug):
- Whitelist specific keys
- Truncate length (e.g. first 100 chars) for long values

### Performance / Latency
Optional: capture duration in wrapper (start timestamp -> response) and log warning if threshold exceeded (frontend perceived latency budget, e.g. > 1200ms) at `warn`.

### Aggregation vs Logging
Prefer metrics counters (custom in-memory tallies) and periodic summarized debug log over line-per-event for high-frequency updates (e.g. streaming sensor updates).

### De-Duplication
Do not re-log an error passed through multiple hooks / components. Responsibility lies with boundary (fetch wrapper OR error boundary).

### Feature Flags
- Introduce boolean guard for verbose logging of chart data transformations (disabled by default).
- Avoid shipping large arrays in console in production.

### Source Maps
Maintain source maps for production builds to make stack traces actionable (ensure they are accessible only internally if privacy constraints apply).

### Evolution
Changes to frontend logging format (prefix, correlation key) must remain backward compatible with any existing parsing tooling before rollout.

### Anti-Patterns
- Using logs for control flow.
- Logging inside tight rendering loops.
- Logging identical warnings on each interval poll.
- Mixing user-visible phrasing in internal diagnostic lines.

### Success Indicators
- Support can reconstruct user-reported failure path from minimal logs.
- Production console free from repetitive noise.
- Debug builds expose sufficient traceability when enabled.
- Clear differentiation of semantic (ApiError subclass) vs transport failures.

---