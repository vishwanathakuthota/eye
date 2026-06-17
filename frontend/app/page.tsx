"use client";

import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RiskLevel = "Low" | "Medium" | "High" | "Critical";
type SourceStatus = "completed" | "partial" | "failed";
type SearchType = "domain" | "ip";

type ApiMeta = {
  request_id: string;
  timestamp: string;
  version: string;
};

type ApiError = {
  code: string;
  message: string;
  details: Record<string, unknown>;
};

type ApiResponse<T> =
  | {
      success: true;
      data: T;
      error: null;
      meta: ApiMeta;
    }
  | {
      success: false;
      data: null;
      error: ApiError;
      meta: ApiMeta;
    };

type DnsRecordType = "A" | "AAAA" | "MX" | "TXT" | "NS" | "CNAME";

type DnsRecords = Record<DnsRecordType, string[]>;

type DomainAnalysis = {
  report_id: string;
  domain: string;
  risk: {
    score: number;
    level: RiskLevel;
    reasons: string[];
    confidence?: number;
    reliability_notes?: string[];
  };
  summary: string;
  dns: {
    records: DnsRecords;
  };
  rdap: Record<string, unknown>;
  certificates: CertificateFinding[];
  subdomains: string[];
  sources: SourceStatusItem[];
  created_at: string;
};

type IpAnalysis = {
  report_id: string;
  ip: string;
  ip_version: number;
  risk: {
    score: number;
    level: RiskLevel;
    reasons: string[];
    confidence?: number;
    reliability_notes?: string[];
  };
  summary: string;
  reverse_dns: {
    ptr_records: string[];
  };
  network: {
    asn: string | null;
    organization: string | null;
    network: string | null;
    classification: string;
    source: string;
    note: string;
    attributes: Record<string, unknown>;
  };
  sources: SourceStatusItem[];
  created_at: string;
};

type ReportSummary = {
  report_id: string;
  type: SearchType;
  target: string;
  risk_level: RiskLevel;
  risk_score: number;
  created_at: string;
};

type ReportList = {
  items: ReportSummary[];
  limit: number;
  offset: number;
  total: number;
};

type ReportDetail = {
  report_id: string;
  type: SearchType;
  target: string;
  payload: DomainAnalysis | IpAnalysis;
};

type CertificateFinding = {
  common_name: string | null;
  name_value: string;
  issuer_name: string | null;
  not_before: string | null;
  not_after: string | null;
};

type SourceStatusItem = {
  name: string;
  status: SourceStatus;
  error?: string | null;
  error_type?: string | null;
  status_code?: number | null;
};

type QueryState =
  | { status: "idle"; result: null; error: null }
  | { status: "loading"; result: null; error: null }
  | { status: "success"; result: DomainAnalysis | IpAnalysis; error: null; searchType: SearchType }
  | { status: "error"; result: null; error: string };

type ReportsState = {
  status: "loading" | "success" | "error";
  items: ReportSummary[];
  error: string | null;
  selectedReportId: string | null;
};

const dnsRecordTypes: DnsRecordType[] = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"];

export default function Home() {
  const [searchType, setSearchType] = useState<SearchType>("domain");
  const [searchValue, setSearchValue] = useState("");
  const [query, setQuery] = useState<QueryState>({
    status: "idle",
    result: null,
    error: null,
  });
  const [reports, setReports] = useState<ReportsState>({
    status: "loading",
    items: [],
    error: null,
    selectedReportId: null,
  });

  const normalizedQuery = useMemo(() => {
    const value = searchValue.trim();
    return searchType === "domain" ? value.toLowerCase() : value;
  }, [searchType, searchValue]);
  const hasResult = query.status === "success";
  const searchLabel = searchType === "domain" ? "Domain" : "IP address";
  const searchPlaceholder = searchType === "domain" ? "example.com" : "8.8.8.8";

  const fetchRecentReports = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reports?limit=10&offset=0`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });
      const body = (await response.json()) as ApiResponse<ReportList>;

      if (!response.ok || !body.success) {
        setReports({
          status: "error",
          items: [],
          error: body.error?.message ?? "Recent reports could not be loaded.",
          selectedReportId: null,
        });
        return;
      }

      setReports({
        status: "success",
        items: body.data.items,
        error: null,
        selectedReportId: null,
      });
    } catch {
      setReports({
        status: "error",
        items: [],
        error: "Eye could not reach the report history API.",
        selectedReportId: null,
      });
    }
  }, []);

  useEffect(() => {
    void fetchRecentReports();
  }, [fetchRecentReports]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!normalizedQuery) {
      setQuery({
        status: "error",
        result: null,
        error: `Enter a ${searchType === "domain" ? "domain" : "valid IP address"} to analyze.`,
      });
      return;
    }

    setQuery({ status: "loading", result: null, error: null });

    try {
      const endpoint =
        searchType === "domain"
          ? `${API_BASE_URL}/domain?domain=${encodeURIComponent(normalizedQuery)}`
          : `${API_BASE_URL}/ip?ip=${encodeURIComponent(normalizedQuery)}`;

      const response = await fetch(
        endpoint,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        },
      );

      const body = (await response.json()) as ApiResponse<DomainAnalysis | IpAnalysis>;

      if (!response.ok || !body.success) {
        setQuery({
          status: "error",
          result: null,
          error: body.error?.message ?? `${searchLabel} analysis failed.`,
        });
        return;
      }

      setQuery({ status: "success", result: body.data, error: null, searchType });
      void fetchRecentReports();
    } catch {
      setQuery({
        status: "error",
        result: null,
        error: "Eye could not reach the Intelligence API.",
      });
    }
  }

  async function handleReportSelect(report: ReportSummary) {
    setReports((current) => ({
      ...current,
      selectedReportId: report.report_id,
      error: null,
    }));
    setQuery({ status: "loading", result: null, error: null });

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${encodeURIComponent(report.report_id)}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        },
      );
      const body = (await response.json()) as ApiResponse<ReportDetail>;

      if (!response.ok || !body.success) {
        setQuery({
          status: "error",
          result: null,
          error: body.error?.message ?? "Report could not be loaded.",
        });
        setReports((current) => ({
          ...current,
          selectedReportId: null,
        }));
        return;
      }

      setSearchType(body.data.type);
      setSearchValue(body.data.target);
      setQuery({
        status: "success",
        result: body.data.payload,
        error: null,
        searchType: body.data.type,
      });
    } catch {
      setQuery({
        status: "error",
        result: null,
        error: "Eye could not reach the report detail API.",
      });
      setReports((current) => ({
        ...current,
        selectedReportId: null,
      }));
    }
  }

  function handleExport(format: "json" | "html") {
    if (query.status !== "success") {
      return;
    }

    const url = `${API_BASE_URL}/reports/${encodeURIComponent(query.result.report_id)}/export/${format}`;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <div>
          <h1>EYE</h1>
          <p className="tagline">Search Anything. Understand Everything.</p>
        </div>
      </header>

      <section className="search-panel" aria-label="Intelligence search">
        <form className="search-form" onSubmit={handleSubmit}>
          <div className="search-heading">
            <label htmlFor="intelligence-search">{searchLabel}</label>
            <div className="search-type-tabs" aria-label="Search type">
              <button
                type="button"
                className={searchType === "domain" ? "active" : ""}
                aria-pressed={searchType === "domain"}
                onClick={() => {
                  setSearchType("domain");
                  setQuery({ status: "idle", result: null, error: null });
                }}
              >
                Domain
              </button>
              <button
                type="button"
                className={searchType === "ip" ? "active" : ""}
                aria-pressed={searchType === "ip"}
                onClick={() => {
                  setSearchType("ip");
                  setQuery({ status: "idle", result: null, error: null });
                }}
              >
                IP
              </button>
            </div>
          </div>
          <div className="search-row">
            <input
              id="intelligence-search"
              name="query"
              type="text"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              placeholder={searchPlaceholder}
              autoComplete="off"
              spellCheck={false}
            />
            <button type="submit" disabled={query.status === "loading"}>
              {query.status === "loading" ? "Analyzing" : "Analyze"}
            </button>
          </div>
        </form>
      </section>

      <RecentReportsPanel reports={reports} onSelect={handleReportSelect} />

      {query.status === "loading" ? <LoadingState /> : null}
      {query.status === "error" ? <ErrorState message={query.error} /> : null}
      {!hasResult && query.status === "idle" ? <EmptyState searchType={searchType} /> : null}

      {hasResult ? (
        <ExportActions reportId={query.result.report_id} onExport={handleExport} />
      ) : null}

      {hasResult && query.searchType === "domain" ? (
        <DomainDashboardResult result={query.result as DomainAnalysis} />
      ) : null}
      {hasResult && query.searchType === "ip" ? (
        <IpDashboardResult result={query.result as IpAnalysis} />
      ) : null}

      <footer className="footer">A product by DrPinnacle</footer>
    </main>
  );
}

function ExportActions({
  reportId,
  onExport,
}: {
  reportId: string;
  onExport: (format: "json" | "html") => void;
}) {
  return (
    <section className="export-actions" aria-label="Report export">
      <div>
        <p className="section-kicker">Export</p>
        <h2>{reportId}</h2>
      </div>
      <div className="export-button-row">
        <button type="button" onClick={() => onExport("json")}>
          JSON
        </button>
        <button type="button" onClick={() => onExport("html")}>
          HTML
        </button>
      </div>
    </section>
  );
}

function RecentReportsPanel({
  reports,
  onSelect,
}: {
  reports: ReportsState;
  onSelect: (report: ReportSummary) => void;
}) {
  const isLoading = reports.status === "loading";

  return (
    <section className="recent-reports" aria-labelledby="recent-reports-heading">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">History</p>
          <h2 id="recent-reports-heading">Recent Reports</h2>
        </div>
        {isLoading ? <span className="history-status">Loading</span> : null}
      </div>

      {reports.status === "error" ? (
        <p className="empty-copy">{reports.error}</p>
      ) : null}

      {reports.status !== "error" && reports.items.length === 0 && !isLoading ? (
        <p className="empty-copy">No reports have been generated yet.</p>
      ) : null}

      {reports.items.length > 0 ? (
        <div className="report-list">
          {reports.items.map((report) => (
            <button
              type="button"
              className="report-row"
              key={report.report_id}
              onClick={() => onSelect(report)}
              disabled={reports.selectedReportId === report.report_id}
            >
              <span className="report-main">
                <strong>{report.target}</strong>
                <span>{report.report_id}</span>
              </span>
              <span className="report-meta">
                <span>{report.type}</span>
                <span>{report.risk_level}</span>
                <span>{report.risk_score}</span>
                <span>{formatDate(report.created_at)}</span>
              </span>
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function RiskCard({ result, subject }: { result: DomainAnalysis | IpAnalysis; subject: string }) {
  const createdAt = formatDate(result.created_at);

  return (
    <section className="score-card" aria-labelledby="risk-heading">
      <div>
        <p className="section-kicker">Risk</p>
        <h2 id="risk-heading">{result.risk.level}</h2>
      </div>
      <div className={`score-ring risk-${result.risk.level.toLowerCase()}`}>
        {result.risk.score}
      </div>
      <div className="score-details">
        <span>Confidence {result.risk.confidence ?? 100}%</span>
        <span>Report {result.report_id}</span>
        <span>{createdAt}</span>
      </div>
      <ListBlock
        items={[...result.risk.reasons, ...(result.risk.reliability_notes ?? [])]}
        emptyLabel={`No risk reasons or reliability notes returned for ${subject}.`}
      />
    </section>
  );
}

function SummaryCard({ result, title }: { result: DomainAnalysis | IpAnalysis; title: string }) {
  return (
    <section className="summary-card" aria-labelledby="summary-heading">
      <p className="section-kicker">Summary</p>
      <h2 id="summary-heading">{title}</h2>
      <p>{result.summary}</p>
    </section>
  );
}

function DomainDashboardResult({ result }: { result: DomainAnalysis }) {
  return (
    <div className="results-grid">
      <RiskCard result={result} subject={result.domain} />
      <SummaryCard result={result} title={result.domain} />
      <Section title="DNS Records">
        <div className="dns-grid">
          {dnsRecordTypes.map((type) => (
            <RecordGroup key={type} label={type} values={result.dns.records[type] ?? []} />
          ))}
        </div>
      </Section>

      <Section title="RDAP">
        <KeyValueData data={result.rdap} emptyLabel="No RDAP data returned." />
      </Section>

      <Section title="Certificate Transparency">
        {result.certificates.length > 0 ? (
          <div className="certificate-list">
            {result.certificates.map((certificate, index) => (
              <article className="certificate-item" key={`${certificate.name_value}-${index}`}>
                <h3>{certificate.common_name ?? "Certificate"}</h3>
                <p>{certificate.name_value}</p>
                <div className="meta-row">
                  <span>{certificate.issuer_name ?? "Unknown issuer"}</span>
                  <span>{certificate.not_before ?? "Unknown start"}</span>
                  <span>{certificate.not_after ?? "Unknown end"}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-copy">No certificate transparency entries returned.</p>
        )}
      </Section>

      <Section title="Subdomains">
        <ListBlock items={result.subdomains} emptyLabel="No subdomains returned." />
      </Section>

      <Section title="Source Status">
        <SourceStatusList sources={result.sources} />
      </Section>
    </div>
  );
}

function IpDashboardResult({ result }: { result: IpAnalysis }) {
  return (
    <div className="results-grid">
      <RiskCard result={result} subject={result.ip} />
      <SummaryCard result={result} title={`${result.ip} IPv${result.ip_version}`} />

      <Section title="Reverse DNS">
        <ListBlock
          items={result.reverse_dns.ptr_records}
          emptyLabel="No PTR records returned."
        />
      </Section>

      <Section title="Network Enrichment">
        <KeyValueData
          data={{
            asn: result.network.asn,
            organization: result.network.organization,
            network: result.network.network,
            classification: result.network.classification,
            source: result.network.source,
            note: result.network.note,
            ...result.network.attributes,
          }}
          emptyLabel="No network enrichment returned."
        />
      </Section>

      <Section title="Source Status">
        <SourceStatusList sources={result.sources} />
      </Section>
    </div>
  );
}

function Section({
  title,
  children,
}: Readonly<{
  title: string;
  children: ReactNode;
}>) {
  return (
    <section className="result-section" aria-labelledby={titleToId(title)}>
      <h2 id={titleToId(title)}>{title}</h2>
      {children}
    </section>
  );
}

function RecordGroup({ label, values }: { label: string; values: string[] }) {
  return (
    <article className="record-group">
      <h3>{label}</h3>
      <ListBlock items={values} emptyLabel="None" />
    </article>
  );
}

function ListBlock({ items, emptyLabel }: { items: string[]; emptyLabel: string }) {
  if (items.length === 0) {
    return <p className="empty-copy">{emptyLabel}</p>;
  }

  return (
    <ul className="data-list">
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>{item}</li>
      ))}
    </ul>
  );
}

function SourceStatusList({ sources }: { sources: SourceStatusItem[] }) {
  if (sources.length === 0) {
    return <p className="empty-copy">No source status returned.</p>;
  }

  return (
    <div className="source-list">
      {sources.map((source) => (
        <article className="source-item" key={source.name}>
          <div>
            <h3>{source.name}</h3>
            <p>{source.error ?? source.error_type ?? "Source completed."}</p>
          </div>
          <span className={`status-pill status-${source.status}`}>{source.status}</span>
        </article>
      ))}
    </div>
  );
}

function KeyValueData({
  data,
  emptyLabel,
}: {
  data: Record<string, unknown>;
  emptyLabel: string;
}) {
  const entries = Object.entries(data).filter(([, value]) => value !== null);

  if (entries.length === 0) {
    return <p className="empty-copy">{emptyLabel}</p>;
  }

  return (
    <dl className="key-value-list">
      {entries.map(([key, value]) => (
        <div key={key} className="key-value-item">
          <dt>{formatKey(key)}</dt>
          <dd>{formatValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function LoadingState() {
  return (
    <section className="state-panel" aria-live="polite">
      <div className="loading-bar" />
      <p>Analyzing passive intelligence sources...</p>
    </section>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <section className="state-panel error-panel" role="alert">
      <strong>Analysis failed</strong>
      <p>{message}</p>
    </section>
  );
}

function EmptyState({ searchType }: { searchType: SearchType }) {
  return (
    <section className="state-panel">
      <strong>Ready</strong>
      <p>
        Enter {searchType === "domain" ? "a domain" : "an IP address"} to generate a local{" "}
        {searchType === "domain" ? "Domain" : "IP"} Intelligence report.
      </p>
    </section>
  );
}

function formatKey(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.length > 0 ? value.map(formatValue).join(", ") : "None";
  }

  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value);
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function titleToId(title: string) {
  return title.toLowerCase().replaceAll(" ", "-");
}
