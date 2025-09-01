# Error & Exception Handling Guidelines (Foundational)

## Purpose
Establish a coherent strategy for classifying, raising, propagating, and presenting errors, aligned with the custom exception hierarchy in `backend/exceptions.py`.

## Objectives
- Provide stable semantic categories (Validation, Not Found, Database, MQTT, Timeout, Generic).
- Preserve internal diagnostic fidelity while exposing sanitized responses.
- Facilitate predictable frontend handling via `error_type`.
- Enable targeted remediation and monitoring.

## Taxonomy Principles
- One class per distinct semantic meaning, not per endpoint.
- Hierarchy depth minimized to avoid cognitive load.
- Shared base (`AppError`) supplies status code and message contract.
- Specialized subclasses refine context without leaking implementation specifics.

## Classification Rules
- ValidationError: Input structure, type, range, or format issues detected early.
- NotFoundError: Definitive absence of a requested resource (no ambiguity).
- Database* Errors: Failures at persistence boundary (connectivity, timeout, generic).
- MQTT* Errors: Broker connectivity or delivery path issues.
- Timeout Errors: True exceeded deadline scenarios only (not generic slowness).
- Generic ApiError: Unexpected but domain-level; still controlled shape.
- AppError fallback: Internal catch-all prior to generic server response.

## Raising Strategy
- Validate early; raise specific exceptions before side effects.
- Wrap third-party/library exceptions once at the boundary (translate to domain exception).
- Maintain original exception context internally (logging) but not in outward message.
- Avoid using generic exceptions for convenience when a specific class exists.

## Propagation
- Allow domain exceptions to bubble to a single centralized handler.
- Do not intercept and re-wrap with equal semantics (avoid semantic erosion).
- Enforce single response emission (no partial writes followed by raise).

## Response Contract
- status: "error"
- error_type: Canonical class name
- message: Concise, user-comprehensible, action-oriented if applicable
- Optional (future): correlation_id, timestamp, documentation link

## Message Guidelines
- Human-readable, bounded length, neutral tone.
- No stack traces, SQL fragments, broker internals, or library identifiers.
- Provide actionable hint for ValidationError (e.g., bounds, expected types).
- Avoid implying existence of other resources in NotFound scenarios.

## Logging Interaction
- Exceptions may self-log at instantiation (current design) OR be centrally logged—never duplicate severity lines.
- Severity alignment derives from exception class category.

## Frontend Consumption
- Branch logic strictly on `error_type`.
- Provide default fallback UX for unknown future classes (forward compatibility).
- Avoid brittle parsing of message text.

## Testing Requirements
- Unit tests assert mapping from raised class to status code and serialized `error_type`.
- Negative tests confirm absence of internal implementation leakage.
- Regression tests ensure new exceptions integrate without altering existing contracts unintentionally.

## Evolution & Governance
Adding a new exception requires:
1. Justification (new semantic gap).
2. Assigned and documented status code (avoid overloading existing ones).
3. Update of hierarchy diagram and this guideline.
4. Relevant test coverage and changelog note.

## Operational Metrics (Optional Future)
Track counts per `error_type` for trend analysis (e.g., ratio of ValidationError vs DatabaseError) to drive quality improvements.

## Anti-Patterns
- Over-granular proliferation (micro-classes with no distinct handling).
- Repurposing a class for unrelated semantics.
- Encoding status codes in message strings.
- Swallowing exceptions silently after logging.
- Using exceptions for nominal control flow.

## Success Indicators
- Frontend can adapt display purely from `error_type`.
- Operational dashboards show stable, interpretable error distribution.
- Minimal need to inspect raw logs for routine client-facing issues.
- Low churn in public error contract

---

## Using the Exceptions (Backend)

### 1. API Resource Layer
Raise domain exceptions directly; do not craft ad-hoc JSON.

```python
from exceptions import ValidationError, NotFoundError
from flask_restful import Resource, reqparse

class DeviceLatest(Resource):
    def get(self, device_id: int):
        if device_id <= 0:
            raise ValidationError("device_id must be positive")
        if not device_exists(device_id):
            raise NotFoundError(f"Device {device_id} not found")
        return {"status": "success", "data": get_latest(device_id)}
```

### 2. Service / Domain Layer
Translate library errors once; propagate typed exception upward.

```python
import psycopg2
from exceptions import DatabaseTimeoutError, DatabaseConnectionError, DatabaseError

def run_query(conn, sql, params):
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except psycopg2.errors.QueryCanceled:
        raise DatabaseTimeoutError("Query exceeded time limit")
    except psycopg2.OperationalError as e:
        raise DatabaseConnectionError(str(e))
    except psycopg2.Error as e:
        raise DatabaseError(e.pgerror or str(e))
```

### 3. MQTT Ingestion
Validate payload early; raise ValidationError; let outer loop decide retry / drop.

```python
from exceptions import ValidationError, DatabaseError

def parse_payload(p):
    if "meta" not in p or "device_id" not in p["meta"]:
        raise ValidationError("Missing device_id")
    if "timestamp" not in p or "value" not in p:
        raise ValidationError("Missing timestamp or value")
    return p["meta"]["device_id"], int(p["timestamp"]), p["value"]
```

### 4. Background / Worker Loop
Catch only high-level base to implement retry/backoff; re-raise unexpected if policy demands.

```python
from exceptions import AppError

def process_message(raw):
    try:
        did, ts, val = parse_payload(raw)
        store(did, ts, val)
    except AppError:
        # Already logged; maybe increment metric / discard
        raise
```

### 5. Global Flask Handler
Single serialization point; no per-endpoint duplication.

```python
from exceptions import AppError
from flask import jsonify

@app.errorhandler(AppError)
def handle_app_error(err: AppError):
    return jsonify({
        "status": "error",
        "error_type": err.__class__.__name__,
        "message": str(err)
    }), getattr(err, "status_code", 500)
```

Fallback for uncaught:

```python
@app.errorhandler(Exception)
def handle_unexpected(err):
    app.logger.exception("Unhandled exception")
    return jsonify({
        "status": "error",
        "error_type": "InternalServerError",
        "message": "An unexpected error occurred"
    }), 500
```

### 6. Frontend Handling Pattern
Map `error_type` to user messages; keep default fallback.

```javascript
function mapBackendError(json) {
  if (json.status !== "error") return null;
  switch (json.error_type) {
    case "ValidationError": return "Input invalid.";
    case "NotFoundError": return "Resource not found.";
    case "DatabaseError": return "Temporary backend issue.";
    default: return json.message || "Unknown error.";
  }
}
```

### 7. Testing Usage
- Mock lower layer to raise each custom exception.
- Assert response status + JSON `error_type`.
- Ensure no stack trace or internal identifiers leak.

```python
def test_validation_error(client, mocker):
    mocker.patch("api.device_data.device_exists", side_effect=ValidationError("bad"))
    r = client.get("/api/devices/1/latest")
    assert r.status_code == 400
    assert r.get_json()["error_type"] == "ValidationError"
```

---

## Adding a New Exception (Python)

### 1. Define
```python
class RateLimitError(ApiError):
    """Too many requests in a given window."""
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, status_code=429)
```

Guidelines:
- Name ends with `Error`.
- Concise one-line docstring.
- Explicit status if diverging from parent.
- Message free of secrets / internal identifiers.

### 2. (Optional) Custom Logging
Override `__init__` only if log level differs from parent.

### 3. Raise at Boundary
Translate from external exception at the outermost integration layer only.

### 4. Serialization
Rely on global handler (do not manually JSONify).

### 5. Update
Docs + tests + (optional) metrics.

### Checklist
- [ ] Correct base class
- [ ] Justified status code
- [ ] Clear message (no sensitive data)
- [ ] Single translation point
- [ ] Tests added
- [ ] Docs updated

---

## Frontend Extension (React)

### Goals
- Mirror backend semantic categories.
- Decouple network / parsing failures from UI components.
- Provide consistent user messaging & developer diagnostics.

### Frontend Taxonomy
```
Error (native)
└─ AppError (base)
   ├─ ApiError (HTTP/status + backend error_type)
   │   ├─ ValidationError
   │   ├─ NotFoundError
   │   ├─ DatabaseError
   │   ├─ DatabaseTimeoutError
   │   ├─ RateLimitError (optional)
   │   └─ GenericApiError
   ├─ NetworkError (connectivity / CORS / abort)
   ├─ ParseError (invalid JSON / schema mismatch)
   ├─ TimeoutError (client-side abort controller)
   └─ UIStateError (unexpected local state invariants)
```

### Class Skeleton
```javascript
// src/errors.js
export class AppError extends Error {
  constructor(message, meta = {}) {
    super(message);
    this.name = this.constructor.name;
    this.meta = meta;
  }
}

export class NetworkError extends AppError {}
export class TimeoutError extends AppError {}
export class ParseError extends AppError {}

export class ApiError extends AppError {
  constructor(message, status, errorType, meta = {}) {
    super(message, { status, errorType, ...meta });
    this.status = status;
    this.errorType = errorType;
  }
}

export class ValidationError extends ApiError {}
export class NotFoundError extends ApiError {}
export class DatabaseError extends ApiError {}
export class DatabaseTimeoutError extends ApiError {}
export class GenericApiError extends ApiError {}
```

### Mapping Backend -> Frontend
| Backend error_type | Frontend class |
|--------------------|----------------|
| ValidationError | ValidationError |
| NotFoundError | NotFoundError |
| DatabaseError | DatabaseError |
| DatabaseTimeoutError | DatabaseTimeoutError |
| (others / unknown) | GenericApiError |

### Fetch Wrapper
Centralize translation; components never call `fetch` directly.

```javascript
// src/api/client.js
import {
  NetworkError, TimeoutError, ParseError,
  ValidationError, NotFoundError,
  DatabaseError, DatabaseTimeoutError,
  GenericApiError
} from "../errors";

const DEFAULT_TIMEOUT_MS = 15000;

function classify(status, errorType, message) {
  switch (errorType) {
    case "ValidationError": return new ValidationError(message, status, errorType);
    case "NotFoundError": return new NotFoundError(message, status, errorType);
    case "DatabaseTimeoutError": return new DatabaseTimeoutError(message, status, errorType);
    case "DatabaseError": return new DatabaseError(message, status, errorType);
    default:
      if (status === 404) return new NotFoundError(message || "Not found", status, "NotFoundError");
      if (status === 400) return new ValidationError(message || "Invalid input", status, "ValidationError");
      return new GenericApiError(message || "Unexpected error", status, errorType || "GenericApiError");
  }
}

export async function apiRequest(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || DEFAULT_TIMEOUT_MS);
  const base = import.meta.env.VITE_API_URL ;
  let res;
  try {
    res = await fetch(base + path, { ...options, signal: controller.signal });
  } catch (e) {
    clearTimeout(timeout);
    if (e.name === "AbortError") throw new TimeoutError("Client-side timeout");
    throw new NetworkError("Network request failed");
  }
  clearTimeout(timeout);

  let body;
  try {
    body = await res.json();
  } catch (e) {
    throw new ParseError("Response JSON invalid");
  }

  if (body.status === "error" || !res.ok) {
    throw classify(res.status, body.error_type, body.message);
  }
  return body;
}
```

### Component Usage Pattern
```javascript
async function loadThresholds() {
  setState(s => ({ ...s, loading: true, error: null }));
  try {
    const json = await apiRequest("/thresholds");
    // process json.data
  } catch (e) {
    if (e instanceof ValidationError) setUserMessage("Eingaben ungültig.");
    else if (e instanceof NotFoundError) setUserMessage("Nicht gefunden.");
    else setUserMessage("Technischer Fehler.");
    setDevError(e); // optional debug state
  } finally {
    setState(s => ({ ...s, loading: false }));
  }
}
```

### UI Messaging Guidelines
| Class | User Message Style |
|-------|--------------------|
| ValidationError | Actionable (what to correct) |
| NotFoundError | Neutral absence message |
| NetworkError | Connectivity hint / retry |
| TimeoutError | Retry suggestion |
| DatabaseError | Generic technical issue |
| GenericApiError | Neutral fallback |

### Error Boundary
Wrap high-level layout to capture render-time UIStateError or unexpected exceptions.

```javascript
class AppErrorBoundary extends React.Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(err) { console.error("[UI]", err); }
  render() { return this.state.hasError ? <Fallback /> : this.props.children; }
}
```

### State Invariant Checks
Throw `UIStateError` (derived from `AppError`) for impossible client-only states; boundary captures and surfaces generic fallback.

### Do / Avoid
- Do: Centralize translation (single fetch wrapper).
- Do: Differentiate network vs backend semantic errors.
- Avoid: Branching on raw `status` codes in components.
- Avoid: Surfacing raw backend messages without sanitization (optional refinement layer).
- Avoid: Silent catch without user feedback.

### Versioning & Evolution
Add new frontend error subclasses only when backend introduces stable new semantic categories or client-only invariants need distinct handling.

---