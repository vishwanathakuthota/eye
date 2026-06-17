# Project Eye Tasks

## Milestone 3 - Report History & Retrieval

Status: Implemented in `feature/report-history`.

- Add `GET /api/v1/reports` for paginated Domain and IP report history.
- Add `GET /api/v1/reports/{report_id}` for stored report detail retrieval.
- Return report summaries with type, target, risk level, risk score, report ID, and creation time.
- Extend the dashboard with a Recent Reports panel.
- Reuse existing Domain and IP result views when loading stored reports.

## Exportable Investigation Reports

Status: Implemented in `feature/report-export`.

- Add JSON export for stored Domain and IP reports.
- Add printable HTML export for stored Domain and IP reports.
- Add dashboard export actions for loaded report details.
- Keep export scope limited to JSON and HTML.

## Intelligence Value Layer

Status: Implemented in `feature/intelligence-value-layer`.

- Add confidence-aware Domain Intelligence scoring with clear incomplete intelligence notes.
- Add email security posture checks for SPF and DMARC, with DKIM reserved as a placeholder.
- Add passive web security header checks, TLS certificate inspection, and basic technology fingerprinting.
- Add structured Intelligence Summary v2 sections and recommendations.
- Extend Domain report JSON and HTML exports with the new intelligence sections.
- Extend the dashboard with intelligence confidence, email security, web security, TLS, infrastructure, and recommendations sections.
