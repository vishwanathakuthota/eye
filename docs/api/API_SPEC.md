# Project Eye API Specification

Version: v0.1.0-alpha

Stage: Intelligence Value Layer

Base path: `/api/v1`

Scope: Domain and IP Intelligence

---

## API Principles

- APIs must be versioned under `/api/v1`.
- APIs must return standard success and error response shapes.
- APIs must validate input before processing.
- APIs must not expose secrets, stack traces, or raw credentials.
- v0.1 APIs are synchronous unless a future roadmap item changes that decision.
- Sprint 002 implements the health endpoint and Domain Intelligence search endpoint.
- Milestone 2 implements the IP Intelligence search endpoint.
- Milestone 3 implements report history and retrieval for Domain and IP reports.
- Exportable Investigation Reports implements JSON and HTML export for stored reports.
- Intelligence Value Layer adds confidence-aware Domain Intelligence, email posture,
  web security headers, TLS inspection, technology fingerprinting, and structured
  recommendations to Domain reports.

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
      "reasons": [],
      "confidence": 100,
      "reliability_notes": []
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
    "intelligence": {
      "intelligence_confidence": "High",
      "incomplete_intelligence": false,
      "confidence_notes": [],
      "email_security": {
        "spf_present": true,
        "spf_record": "v=spf1 include:_spf.example.com -all",
        "dmarc_present": true,
        "dmarc_record": "v=DMARC1; p=reject",
        "dkim_status": "placeholder",
        "score": 100,
        "findings": [],
        "recommendations": []
      },
      "web_security": {
        "checked_url": "https://example.com/",
        "status_code": 200,
        "headers": [
          {
            "name": "Strict-Transport-Security",
            "present": true,
            "value": "max-age=31536000",
            "recommendation": null
          }
        ],
        "score": 100,
        "findings": [],
        "recommendations": []
      },
      "tls": {
        "checked_host": "example.com",
        "issuer": "Example CA",
        "subject": "example.com",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2026-12-31T23:59:59Z",
        "days_remaining": 197,
        "status": "valid",
        "findings": [],
        "recommendations": []
      },
      "technology": {
        "server": "cloudflare",
        "powered_by": null,
        "cdn_or_security": [
          "Cloudflare"
        ],
        "findings": [
          "Server header reports cloudflare."
        ]
      },
      "recommendations": [],
      "summary_v2": {
        "executive_summary": {
          "title": "Executive Summary",
          "body": "example.com has Low observed risk with High intelligence confidence.",
          "bullets": []
        },
        "attack_surface_snapshot": {
          "title": "Attack Surface Snapshot",
          "body": "DNS, RDAP, certificate transparency, web, and TLS sources were reviewed.",
          "bullets": []
        },
        "email_security": {
          "title": "Email Security",
          "body": "Email security posture score is 100/100.",
          "bullets": []
        },
        "web_security": {
          "title": "Web Security",
          "body": "Web security header posture score is 100/100.",
          "bullets": []
        },
        "infrastructure": {
          "title": "Infrastructure",
          "body": "Observed infrastructure indicators are summarized from passive sources.",
          "bullets": []
        },
        "confidence_notes": {
          "title": "Confidence Notes",
          "body": "Intelligence confidence is High.",
          "bullets": []
        },
        "recommendations": {
          "title": "Recommendations",
          "body": "No recommendations returned.",
          "bullets": []
        }
      }
    },
    "sources": [
      {
        "name": "dns",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "rdap",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "crt.sh",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "email_security",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "web_security",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "tls",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
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

### Source Reliability

Domain analysis responses include source status metadata so clients can distinguish observed intelligence from upstream source reliability issues.

Source status values:

- `completed`: Source returned a usable response.
- `partial`: Source returned usable data, but the response was capped or incomplete.
- `failed`: Source did not return usable data.

Source failure `error_type` values:

- `not_found`: Source completed the lookup and found no matching record.
- `timeout`: Source timed out.
- `rate_limited`: Source returned a rate-limit response.
- `server_error`: Source returned a 5xx response.
- `http_error`: Source returned another non-success HTTP response.
- `invalid_response`: Source returned malformed or unexpected data.
- `unexpected_error`: Source failed unexpectedly.

Risk scoring remains focused on observed intelligence. Transient source failures such as timeouts, rate limits, and upstream server errors should be represented in `sources`, `risk.reliability_notes`, and `intelligence.confidence_notes`; they should not be treated as strong security findings. `risk.confidence` is a 0-100 indicator of how complete the source coverage was for the score.

### Intelligence Value Layer

Domain responses include an `intelligence` object:

- `intelligence_confidence`: `High`, `Medium`, or `Low` coverage confidence.
- `incomplete_intelligence`: `true` when major source failures make the report incomplete.
- `confidence_notes`: Reader-facing notes about source reliability and coverage.
- `email_security`: SPF, DMARC, DKIM placeholder status, posture score, findings, and recommendations.
- `web_security`: Passive HTTP/HTTPS header posture for HSTS, CSP, X-Frame-Options, X-Content-Type-Options, and Referrer-Policy.
- `tls`: Live TLS certificate issuer, subject, validity window, days remaining, status, findings, and recommendations when retrievable.
- `technology`: Basic server, powered-by, CDN, or security header indicators.
- `recommendations`: Consolidated remediation recommendations.
- `summary_v2`: Structured executive summary, attack surface, email security, web security, infrastructure, confidence notes, and recommendations sections.

If a major source fails, the API should clearly represent incomplete intelligence without falsely lowering observed risk.

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

## GET /api/v1/ip?ip=<ip_address>

Runs passive IP Intelligence analysis for an IPv4 or IPv6 address.

Status: Implemented in Milestone 2.

### Request Example

```bash
curl "http://localhost:8000/api/v1/ip?ip=8.8.8.8"
```

### Query Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `ip` | string | Yes | IPv4 or IPv6 address to analyze. Example: `8.8.8.8` |

### Response Example

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "report_id": "ipr_123",
    "ip": "8.8.8.8",
    "ip_version": 4,
    "risk": {
      "score": 5,
      "level": "Low",
      "reasons": [],
      "confidence": 100,
      "reliability_notes": []
    },
    "summary": "8.8.8.8 was analyzed as an IPv4 address using local IP Intelligence sources.",
    "reverse_dns": {
      "ptr_records": [
        "dns.google."
      ]
    },
    "network": {
      "asn": null,
      "organization": null,
      "network": null,
      "classification": "global",
      "source": "local-placeholder",
      "note": "ASN and network ownership enrichment is reserved for a future integration.",
      "attributes": {
        "is_global": true,
        "is_private": false,
        "is_reserved": false,
        "is_loopback": false,
        "is_multicast": false,
        "is_link_local": false,
        "reverse_pointer": "8.8.8.8.in-addr.arpa"
      }
    },
    "sources": [
      {
        "name": "reverse_dns",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      },
      {
        "name": "network_enrichment",
        "status": "completed",
        "error": null,
        "error_type": null,
        "status_code": null
      }
    ],
    "created_at": "2026-06-17T00:00:00Z"
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-17T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

### Persistence

A successful response is persisted to PostgreSQL before the API returns `200 OK`.

### Source Reliability

IP analysis responses include source status metadata. Reverse DNS timeouts and resolver failures are visible in `sources` and may reduce `risk.confidence`, but they are not treated as strong risk findings by themselves.

### Error Example

Status: `422 Unprocessable Entity`

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "IP_INVALID",
    "message": "IP address must be a valid IPv4 or IPv6 address.",
    "details": {
      "field": "ip"
    }
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-17T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## GET /api/v1/reports

Returns paginated report history across Domain and IP Intelligence reports.

Status: Implemented in Milestone 3.

### Request Example

```bash
curl "http://localhost:8000/api/v1/reports?limit=20&offset=0"
```

### Query Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `limit` | integer | No | `20` | Number of reports to return. Minimum `1`, maximum `100`. |
| `offset` | integer | No | `0` | Number of reports to skip. Minimum `0`. |

### Response Example

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "report_id": "ipr_123",
        "type": "ip",
        "target": "8.8.8.8",
        "risk_level": "Low",
        "risk_score": 5,
        "created_at": "2026-06-17T00:00:00Z"
      },
      {
        "report_id": "rep_123",
        "type": "domain",
        "target": "example.com",
        "risk_level": "Low",
        "risk_score": 20,
        "created_at": "2026-06-16T00:00:00Z"
      }
    ],
    "limit": 20,
    "offset": 0,
    "total": 2
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-17T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

### Error Example

Status: `422 Unprocessable Entity`

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request is invalid.",
    "details": {
      "errors": []
    }
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-17T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## GET /api/v1/reports/{report_id}

Returns a stored intelligence report.

Status: Implemented in Milestone 3.

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
    "type": "domain",
    "target": "example.com",
    "payload": {
      "report_id": "rep_123",
      "domain": "example.com",
      "risk": {
        "score": 20,
        "level": "Low",
        "reasons": [],
        "confidence": 100,
        "reliability_notes": []
      },
      "summary": "Passive domain intelligence summary.",
      "dns": {},
      "rdap": {},
      "certificates": [],
      "subdomains": [],
      "sources": [],
      "created_at": "2026-06-16T00:00:00Z"
    }
  },
  "error": null,
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-16T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

For IP reports, `type` is `ip`, `target` is the IP address, and `payload` uses the same shape returned by `GET /api/v1/ip`.

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

Invalid report IDs return:

Status: `422 Unprocessable Entity`

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "REPORT_INVALID",
    "message": "Report ID is invalid.",
    "details": {
      "field": "report_id"
    }
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-06-17T00:00:00Z",
    "version": "v0.1.0-alpha"
  }
}
```

---

## GET /api/v1/reports/{report_id}/export/json

Exports a stored Domain or IP report as a JSON investigation document.

Status: Implemented in Exportable Investigation Reports.

### Request Example

```bash
curl "http://localhost:8000/api/v1/reports/rep_123/export/json"
```

### Response Example

Status: `200 OK`

Headers:

```http
Content-Type: application/json
Content-Disposition: attachment; filename="eye-rep_123.json"
```

```json
{
  "metadata": {
    "product": "Eye",
    "exported_at": "2026-06-17T00:00:00Z",
    "format": "json",
    "report_id": "rep_123",
    "type": "domain",
    "target": "example.com",
    "created_at": "2026-06-16T00:00:00Z"
  },
  "report": {
    "report_id": "rep_123",
    "domain": "example.com",
    "risk": {
      "score": 20,
      "level": "Low",
      "reasons": [],
      "confidence": 100,
      "reliability_notes": []
    },
    "summary": "Passive domain intelligence summary.",
    "dns": {},
    "rdap": {},
    "certificates": [],
    "subdomains": [],
    "sources": [],
    "intelligence": {
      "intelligence_confidence": "High",
      "incomplete_intelligence": false,
      "confidence_notes": [],
      "email_security": {},
      "web_security": {},
      "tls": null,
      "technology": {},
      "recommendations": [],
      "summary_v2": null
    },
    "created_at": "2026-06-16T00:00:00Z"
  }
}
```

Unknown report IDs return `REPORT_NOT_FOUND`. Invalid report IDs return `REPORT_INVALID`.

---

## GET /api/v1/reports/{report_id}/export/html

Exports a stored Domain or IP report as a printable HTML executive investigation report.

Status: Implemented in Exportable Investigation Reports.

### Request Example

```bash
curl "http://localhost:8000/api/v1/reports/rep_123/export/html"
```

### Response Example

Status: `200 OK`

Headers:

```http
Content-Type: text/html; charset=utf-8
Content-Disposition: inline; filename="eye-rep_123.html"
```

The HTML response contains:

- Report metadata.
- Risk score, level, confidence, risk reasons, and reliability notes.
- Executive summary.
- Domain findings or IP findings depending on report type.
- Intelligence confidence, email security, web security, TLS, technology, and recommendations for Domain reports when available.
- Source status.

HTML export output must escape report data before rendering it into markup.

Unknown report IDs return `REPORT_NOT_FOUND`. Invalid report IDs return `REPORT_INVALID`.

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

### IP Validation

The `ip` query parameter must:

- Be present.
- Be a string.
- Be trimmed before validation.
- Parse as a valid IPv4 or IPv6 address.
- Be normalized using standard IP address formatting.

The `ip` query parameter must reject:

- Empty values.
- Domain names.
- URLs with schemes, paths, queries, or fragments.
- CIDR ranges.
- IP addresses with ports.
- Whitespace-separated values.
- Shell syntax.
- Script content.

### Report ID Validation

The `report_id` path parameter must:

- Be present.
- Be a string.
- Match the server-defined report identifier format.
- Reject path traversal sequences.
- Reject whitespace.

Report export endpoints use the same report ID validation rules.

### Report Pagination Validation

The `GET /api/v1/reports` query parameters must:

- Use `limit` as an integer from `1` through `100`.
- Use `offset` as an integer greater than or equal to `0`.
- Return `VALIDATION_ERROR` for invalid query parameter types or ranges.

---

## HTTP Status Codes

| Status | Meaning | Usage |
| --- | --- | --- |
| `200 OK` | Successful request | Health, domain analysis, IP analysis, report retrieval, report export |
| `400 Bad Request` | Invalid request shape | Missing or malformed request |
| `404 Not Found` | Resource not found | Report ID does not exist |
| `408 Request Timeout` | Request timed out | Analysis or dependency timeout |
| `422 Unprocessable Entity` | Validation failed | Unsupported domain, IP address, or report identifier |
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
- `IP_INVALID`
- `REPORT_INVALID`
- `REPORT_NOT_FOUND`
- `RATE_LIMITED`
- `ANALYSIS_TIMEOUT`
- `EXTERNAL_SOURCE_ERROR`
- `DATABASE_ERROR`
- `INTERNAL_ERROR`
