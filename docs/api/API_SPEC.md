# Project Eye API Specification

Version: v0.1.0-alpha

Stage: Sprint 002 - Domain Intelligence Engine

Base path: `/api/v1`

Scope: Domain Intelligence only

---

## API Principles

- APIs must be versioned under `/api/v1`.
- APIs must return standard success and error response shapes.
- APIs must validate input before processing.
- APIs must not expose secrets, stack traces, or raw credentials.
- v0.1 APIs are synchronous unless a future roadmap item changes that decision.
- Sprint 002 implements the health endpoint and Domain Intelligence search endpoint.
- Report retrieval remains planned until a later sprint.

---

## Standard Success Response

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

Fields:

- `success`: Always `true` for successful responses.
- `data`: Endpoint-specific payload.
- `error`: Always `null` for successful responses.
- `meta.request_id`: Unique request identifier.
- `meta.timestamp`: Server response timestamp in ISO 8601 format.
- `meta.version`: API or product version.

---

## Standard Error Response

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request is invalid.",
    "details": {}
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

Fields:

- `success`: Always `false` for failed responses.
- `data`: Always `null` for failed responses.
- `error.code`: Stable machine-readable error code.
- `error.message`: Safe human-readable message.
- `error.details`: Optional structured details safe for clients.
- `meta.request_id`: Unique request identifier.
- `meta.timestamp`: Server response timestamp in ISO 8601 format.
- `meta.version`: API or product version.

---

## GET /api/v1/health

Returns API health for local development and release validation.

### Request Example

```bash
curl http://localhost:8000/api/v1/health
```

### Response Example

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "eye-api",
    "version": "v0.1.0-alpha"
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

### Error Example

If the service is unavailable, clients may receive:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "The API service is unavailable.",
    "details": {}
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## GET /api/v1/domain?domain=<domain>

Runs passive Domain Intelligence analysis for a domain.

Status: Implemented in Sprint 002.

### Request Example

```bash
curl "http://localhost:8000/api/v1/domain?domain=example.com"
```

### Query Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `domain` | string | Yes | Domain to analyze. Example: `example.com` |

### Response Example

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "report_id": "rep_123",
    "domain": "example.com",
    "risk": {
      "score": 20,
      "level": "Low",
      "reasons": []
    },
    "summary": "Passive domain intelligence summary.",
    "dns": {
      "records": {
        "A": [],
        "AAAA": [],
        "MX": [],
        "TXT": [],
        "NS": [],
        "CNAME": []
      }
    },
    "rdap": {},
    "certificates": [],
    "subdomains": [],
    "sources": [
      {
        "name": "dns",
        "status": "completed"
      },
      {
        "name": "rdap",
        "status": "completed"
      },
      {
        "name": "crt.sh",
        "status": "completed"
      }
    ],
    "created_at": "2026-06-16T00:00:00Z"
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

### Persistence

A successful response is persisted to PostgreSQL before the API returns `200 OK`.

### Error Example

Status: `422 Unprocessable Entity`

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DOMAIN_INVALID",
    "message": "Domain must be a valid hostname.",
    "details": {
      "field": "domain"
    }
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## GET /api/v1/reports/{report_id}

Returns a stored Domain Intelligence report.

Status: Planned for a later sprint. Not implemented in Sprint 002.

### Request Example

```bash
curl http://localhost:8000/api/v1/reports/rep_123
```

### Path Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `report_id` | string | Yes | Stored report identifier. |

### Response Example

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "report_id": "rep_123",
    "domain": "example.com",
    "risk": {
      "score": 20,
      "level": "Low",
      "reasons": []
    },
    "summary": "Passive domain intelligence summary.",
    "dns": {},
    "rdap": {},
    "certificates": [],
    "subdomains": [],
    "sources": [],
    "created_at": "2026-06-16T00:00:00Z"
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

### Error Example

Status: `404 Not Found`

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "REPORT_NOT_FOUND",
    "message": "Report was not found.",
    "details": {
      "report_id": "rep_123"
    }
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## Validation Rules

### Domain Validation

The `domain` query parameter must:

- Be present.
- Be a string.
- Be trimmed before validation.
- Be normalized to lowercase.
- Be a hostname, not a URL.
- Contain at least one dot.
- Use valid DNS label characters.
- Be no longer than 253 characters.
- Have no label longer than 63 characters.

The `domain` query parameter must reject:

- Empty values.
- URLs with schemes, paths, queries, or fragments.
- IP addresses.
- `localhost`.
- Private network targets.
- Email addresses.
- Wildcards.
- Whitespace.
- Shell syntax.
- Script content.

### Report ID Validation

The `report_id` path parameter must:

- Be present.
- Be a string.
- Match the server-defined report identifier format.
- Reject path traversal sequences.
- Reject whitespace.

---

## HTTP Status Codes

| Status | Meaning | Usage |
| --- | --- | --- |
| `200 OK` | Successful request | Health, domain analysis, report retrieval |
| `400 Bad Request` | Invalid request shape | Missing or malformed request |
| `404 Not Found` | Resource not found | Report ID does not exist |
| `408 Request Timeout` | Request timed out | Analysis or dependency timeout |
| `422 Unprocessable Entity` | Validation failed | Unsupported domain or report identifier |
| `429 Too Many Requests` | Rate limited | Request exceeds configured limits |
| `500 Internal Server Error` | Unexpected server failure | Unhandled backend error |
| `502 Bad Gateway` | External source failure | Passive source failed unexpectedly |
| `503 Service Unavailable` | Service unavailable | API or dependency unavailable |

---

## Error Codes

Initial stable error codes:

- `SERVICE_UNAVAILABLE`
- `VALIDATION_ERROR`
- `DOMAIN_REQUIRED`
- `DOMAIN_INVALID`
- `REPORT_NOT_FOUND`
- `RATE_LIMITED`
- `ANALYSIS_TIMEOUT`
- `EXTERNAL_SOURCE_ERROR`
- `DATABASE_ERROR`
- `INTERNAL_ERROR`
