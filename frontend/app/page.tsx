"use client";

import { FormEvent, ReactNode, useMemo, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RiskLevel = "Low" | "Medium" | "High" | "Critical";
type SourceStatus = "completed" | "partial" | "failed";

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
  | { status: "success"; result: DomainAnalysis; error: null }
  | { status: "error"; result: null; error: string };

const dnsRecordTypes: DnsRecordType[] = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"];

export default function Home() {
  const [domain, setDomain] = useState("");
  const [query, setQuery] = useState<QueryState>({
    status: "idle",
    result: null,
    error: null,
  });

  const normalizedDomain = useMemo(() => domain.trim().toLowerCase(), [domain]);
  const hasResult = query.status === "success";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!normalizedDomain) {
      setQuery({
        status: "error",
        result: null,
        error: "Enter a domain to analyze.",
      });
      return;
    }

    setQuery({ status: "loading", result: null, error: null });

    try {
      const response = await fetch(
        `${API_BASE_URL}/domain?domain=${encodeURIComponent(normalizedDomain)}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        },
      );
      const body = (await response.json()) as ApiResponse<DomainAnalysis>;

      if (!response.ok || !body.success) {
        setQuery({
          status: "error",
          result: null,
          error: body.error?.message ?? "Domain analysis failed.",
        });
        return;
      }

      setQuery({ status: "success", result: body.data, error: null });
    } catch {
      setQuery({
        status: "error",
        result: null,
        error: "Eye could not reach the Domain Intelligence API.",
      });
    }
  }

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <div>
          <p className="version">v0.1.0-alpha</p>
          <h1>Eye</h1>
          <p className="tagline">Search Anything. Understand Everything.</p>
        </div>
        <div className="api-chip">Domain Intelligence</div>
      </header>

      <section className="search-panel" aria-label="Domain search">
        <form className="search-form" onSubmit={handleSubmit}>
          <label htmlFor="domain-search">Domain</label>
          <div className="search-row">
            <input
              id="domain-search"
              name="domain"
              type="text"
              value={domain}
              onChange={(event) => setDomain(event.target.value)}
              placeholder="example.com"
              autoComplete="off"
              spellCheck={false}
            />
            <button type="submit" disabled={query.status === "loading"}>
              {query.status === "loading" ? "Analyzing" : "Analyze"}
            </button>
          </div>
        </form>
      </section>

      {query.status === "loading" ? <LoadingState /> : null}
      {query.status === "error" ? <ErrorState message={query.error} /> : null}
      {!hasResult && query.status === "idle" ? <EmptyState /> : null}

      {hasResult ? <DashboardResult result={query.result} /> : null}
    <main className="shell">
      <section className="intro" aria-labelledby="product-name">
        <h1 id="product-name">Eye</h1>
        <p className="tagline">Search Anything. Understand Everything.</p>
      </section>
      <footer className="footer">A product by DrPinnacle</footer>
    </main>
  );
}

function DashboardResult({ result }: { result: DomainAnalysis }) {
  const createdAt = new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(result.created_at));

  return (
    <div className="results-grid">
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
          emptyLabel="No risk reasons or reliability notes returned."
        />
      </section>

      <section className="summary-card" aria-labelledby="summary-heading">
        <p className="section-kicker">Summary</p>
        <h2 id="summary-heading">{result.domain}</h2>
        <p>{result.summary}</p>
      </section>

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
        <div className="source-list">
          {result.sources.map((source) => (
            <article className="source-item" key={source.name}>
              <div>
                <h3>{source.name}</h3>
                <p>{source.error ?? source.error_type ?? "Source completed."}</p>
              </div>
              <span className={`status-pill status-${source.status}`}>{source.status}</span>
            </article>
          ))}
        </div>
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

function EmptyState() {
  return (
    <section className="state-panel">
      <strong>Ready</strong>
      <p>Enter a domain to generate the first local Domain Intelligence report.</p>
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

function titleToId(title: string) {
  return title.toLowerCase().replaceAll(" ", "-");
}
