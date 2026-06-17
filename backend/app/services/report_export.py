from __future__ import annotations

import html
from datetime import UTC, datetime
from typing import Any, Literal

from app.schemas.report import ReportDetailResult

ExportFormat = Literal["json", "html"]


class ReportExportService:
    def build_json_export(self, report: ReportDetailResult) -> dict[str, Any]:
        payload = report.payload.model_dump(mode="json")
        return {
            "metadata": {
                "product": "Eye",
                "exported_at": _utc_now_iso(),
                "format": "json",
                "report_id": report.report_id,
                "type": report.type,
                "target": report.target,
                "created_at": payload["created_at"],
            },
            "report": payload,
        }

    def build_html_export(self, report: ReportDetailResult) -> str:
        payload = report.payload.model_dump(mode="json")
        target = _escape(report.target)
        report_type = _escape(_display_report_type(report.type))
        risk = payload["risk"]
        findings = _findings_for_report(report.type, payload)
        reliability_notes = _list_section(
            "Reliability Notes",
            risk.get("reliability_notes", []),
            "No reliability notes returned.",
        )

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eye Investigation Report - {target}</title>
  <style>
    :root {{
      color-scheme: light;
      --border: #d8dee8;
      --foreground: #111827;
      --muted: #5b6472;
      --surface-muted: #f8fafc;
      --accent: #0f766e;
    }}
    body {{
      margin: 0;
      background: #ffffff;
      color: var(--foreground);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(940px, 100%);
      margin: 0 auto;
      padding: 36px 24px;
    }}
    header {{
      border-bottom: 2px solid var(--border);
      margin-bottom: 24px;
      padding-bottom: 18px;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 34px; line-height: 1.1; }}
    h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
    .meta, .risk, .section {{
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 18px;
      padding: 16px;
    }}
    .meta, .risk {{ background: var(--surface-muted); }}
    dl {{ display: grid; grid-template-columns: 180px 1fr; gap: 8px 14px; margin: 0; }}
    dt {{ color: var(--muted); font-weight: 700; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    ul {{ margin: 0; padding-left: 20px; }}
    pre {{
      background: var(--surface-muted);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
      padding: 12px;
      white-space: pre-wrap;
    }}
    .brand {{ color: var(--accent); font-weight: 800; text-transform: uppercase; }}
    @media print {{
      main {{ padding: 0; width: 100%; }}
      .meta, .risk, .section {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="brand">Eye</p>
      <h1>Executive Investigation Report</h1>
      <p>{report_type} intelligence report for <strong>{target}</strong>.</p>
    </header>
    <section class="meta">
      <h2>Report Metadata</h2>
      <dl>
        <dt>Report ID</dt><dd>{_escape(report.report_id)}</dd>
        <dt>Type</dt><dd>{report_type}</dd>
        <dt>Target</dt><dd>{target}</dd>
        <dt>Created</dt><dd>{_escape(payload["created_at"])}</dd>
        <dt>Exported</dt><dd>{_escape(_utc_now_iso())}</dd>
      </dl>
    </section>
    <section class="risk">
      <h2>Risk</h2>
      <dl>
        <dt>Level</dt><dd>{_escape(risk["level"])}</dd>
        <dt>Score</dt><dd>{_escape(str(risk["score"]))}</dd>
        <dt>Confidence</dt><dd>{_escape(str(risk.get("confidence", 100)))}%</dd>
      </dl>
      {_list_section("Risk Reasons", risk.get("reasons", []), "No risk reasons returned.")}
      {reliability_notes}
    </section>
    <section class="section">
      <h2>Executive Summary</h2>
      <p>{_escape(payload["summary"])}</p>
    </section>
    {findings}
    <section class="section">
      <h2>Source Status</h2>
      {_source_status(payload.get("sources", []))}
    </section>
  </main>
</body>
</html>"""


def _findings_for_report(report_type: str, payload: dict[str, Any]) -> str:
    if report_type == "domain":
        dns_records = payload.get("dns", {}).get("records", {})
        return f"""
    <section class="section">
      <h2>DNS Records</h2>
      {_keyed_lists(dns_records)}
    </section>
    <section class="section">
      <h2>RDAP</h2>
      {_json_block(payload.get("rdap", {}))}
    </section>
    <section class="section">
      <h2>Certificate Transparency</h2>
      {_json_block(payload.get("certificates", []))}
    </section>
    <section class="section">
      <h2>Subdomains</h2>
      {_simple_list(payload.get("subdomains", []), "No subdomains returned.")}
    </section>"""

    ptr_records = payload.get("reverse_dns", {}).get("ptr_records", [])
    return f"""
    <section class="section">
      <h2>Reverse DNS</h2>
      {_simple_list(ptr_records, "No PTR records returned.")}
    </section>
    <section class="section">
      <h2>Network Enrichment</h2>
      {_json_block(payload.get("network", {}))}
    </section>"""


def _source_status(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "<p>No source status returned.</p>"

    items = [
        f"{source.get('name', 'unknown')}: "
        f"{source.get('status', 'unknown')}"
        f"{' - ' + source['error'] if source.get('error') else ''}"
        for source in sources
    ]
    return _simple_list(items, "No source status returned.")


def _keyed_lists(values: dict[str, list[str]]) -> str:
    if not values:
        return "<p>No DNS records returned.</p>"

    rows = []
    for key, records in values.items():
        rows.append(f"<h3>{_escape(key)}</h3>{_simple_list(records, 'None')}")
    return "".join(rows)


def _simple_list(values: list[Any], empty_label: str) -> str:
    if not values:
        return f"<p>{_escape(empty_label)}</p>"

    items = "".join(f"<li>{_escape(str(value))}</li>" for value in values)
    return f"<ul>{items}</ul>"


def _list_section(title: str, values: list[str], empty_label: str) -> str:
    return f"<h3>{_escape(title)}</h3>{_simple_list(values, empty_label)}"


def _json_block(value: Any) -> str:
    return f"<pre>{_escape_json(value)}</pre>"


def _escape_json(value: Any) -> str:
    import json

    return _escape(json.dumps(value, indent=2, sort_keys=True))


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _display_report_type(report_type: str) -> str:
    if report_type == "ip":
        return "IP"
    return "Domain"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
