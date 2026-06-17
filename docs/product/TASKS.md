# Project Eye Tasks

## Milestone 3 - Report History & Retrieval

Status: Implemented in `feature/report-history`.

- Add `GET /api/v1/reports` for paginated Domain and IP report history.
- Add `GET /api/v1/reports/{report_id}` for stored report detail retrieval.
- Return report summaries with type, target, risk level, risk score, report ID, and creation time.
- Extend the dashboard with a Recent Reports panel.
- Reuse existing Domain and IP result views when loading stored reports.
