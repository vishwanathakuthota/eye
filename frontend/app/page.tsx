"use client";

import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RiskLevel = "Low" | "Medium" | "High" | "Critical";
type SourceStatus = "completed" | "partial" | "failed";
type SearchType = "domain" | "ip";
type IntelligenceConfidence = "High" | "Medium" | "Low";

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
  intelligence?: IntelligenceValueLayer;
  created_at: string;
};

type IntelligenceSectionData = {
  title: string;
  body: string;
  bullets: string[];
};

type IntelligenceValueLayer = {
  intelligence_confidence: IntelligenceConfidence;
  incomplete_intelligence: boolean;
  confidence_notes: string[];
  email_security: {
    spf_present: boolean;
    spf_record: string | null;
    dmarc_present: boolean;
    dmarc_record: string | null;
    dkim_status: string;
    score: number;
    findings: string[];
    recommendations: string[];
  };
  web_security: {
    checked_url: string | null;
    status_code: number | null;
    headers: {
      name: string;
      present: boolean;
      value: string | null;
      recommendation: string | null;
    }[];
    score: number;
    findings: string[];
    recommendations: string[];
  };
  tls: {
    checked_host: string;
    issuer: string | null;
    subject: string | null;
    valid_from: string | null;
    valid_to: string | null;
    days_remaining: number | null;
    status: string;
    findings: string[];
    recommendations: string[];
  } | null;
  technology: {
    server: string | null;
    powered_by: string | null;
    cdn_or_security: string[];
    findings: string[];
  };
  recommendations: string[];
  summary_v2: {
    executive_summary: IntelligenceSectionData;
    attack_surface_snapshot: IntelligenceSectionData;
    email_security: IntelligenceSectionData;
    web_security: IntelligenceSectionData;
    infrastructure: IntelligenceSectionData;
    confidence_notes: IntelligenceSectionData;
    recommendations: IntelligenceSectionData;
  } | null;
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
const exampleSearches = ["Elon Musk", "Tesla", "techoptima.ai", "8.8.8.8"];
const pricingPlans = [
  {
    name: "Free",
    description: "Start with lightweight public intelligence lookups.",
    features: ["10 searches/month", "Domain and IP intelligence", "Basic reports"],
  },
  {
    name: "Pro",
    description: "For individual investigators who need repeatable reports.",
    features: [
      "500 searches/month",
      "Person/company intelligence when available",
      "Report history",
      "JSON/HTML exports",
    ],
    featured: true,
  },
  {
    name: "Team",
    description: "Coordinate investigations across a small analyst group.",
    features: ["Shared investigations", "Watchlists later", "Team workspace later"],
  },
  {
    name: "Enterprise",
    description: "Bring Eye into governed environments and custom workflows.",
    features: ["API access", "Private deployment", "Custom data connectors", "SLA/support"],
  },
];

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

    const detectedSearchType = detectSearchType(normalizedQuery);
    if (!detectedSearchType) {
      setQuery({
        status: "error",
        result: null,
        error:
          "Person, company, email, and organization intelligence are not available in this local alpha yet. Try a domain or IP address.",
      });
      return;
    }

    setSearchType(detectedSearchType);
    setQuery({ status: "loading", result: null, error: null });

    try {
      const endpoint =
        detectedSearchType === "domain"
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
          error:
            body.error?.message ??
            `${detectedSearchType === "domain" ? "Domain" : "IP"} analysis failed.`,
        });
        return;
      }

      setQuery({
        status: "success",
        result: body.data,
        error: null,
        searchType: detectedSearchType,
      });
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
          <p className="brand-kicker">AI-Native Intelligence Search Engine</p>
          <h1>Eye</h1>
          <p className="tagline">Search Anything. Understand Everything.</p>
        </div>
        <span className="api-chip">Domain/IP live</span>
      </header>

      <section className="hero-panel" aria-labelledby="hero-heading">
        <div className="hero-copy">
          <p className="section-kicker">Intelligence Search</p>
          <h2 id="hero-heading">Search people, companies, domains, IPs, and digital assets.</h2>
          <p>
            Turn public information into actionable intelligence. Eye starts with
            local Domain and IP intelligence today, then expands into a broader
            investigative search workspace.
          </p>
        </div>
        <form className="search-form" onSubmit={handleSubmit}>
          <div className="search-heading">
            <label htmlFor="intelligence-search">Unified Search</label>
            <div className="search-scope" aria-label="Available search types">
              <span className={searchType === "domain" ? "active" : ""}>Domain</span>
              <span className={searchType === "ip" ? "active" : ""}>IP</span>
              <span>People later</span>
              <span>Companies later</span>
            </div>
          </div>
          <div className="search-row unified-search-row">
            <input
              id="intelligence-search"
              name="query"
              type="text"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              placeholder="Search person, company, domain, IP, email, or organization"
              autoComplete="off"
              spellCheck={false}
            />
            <button type="submit" disabled={query.status === "loading"}>
              {query.status === "loading" ? "Searching" : "Search"}
            </button>
          </div>
          <div className="example-row" aria-label="Example searches">
            <span>Examples</span>
            {exampleSearches.map((example) => (
              <button
                key={example}
                type="button"
                className="example-chip"
                onClick={() => {
                  setSearchValue(example);
                  setSearchType(detectSearchType(example) ?? "domain");
                  setQuery({ status: "idle", result: null, error: null });
                }}
              >
                {example}
              </button>
            ))}
          </div>
        </form>
      </section>

      <section className="positioning-grid" aria-label="Product positioning">
        <article>
          <strong>Unified search</strong>
          <span>One command surface for public intelligence workflows.</span>
        </article>
        <article>
          <strong>Actionable reports</strong>
          <span>Risk, source status, summaries, history, and exports in one place.</span>
        </article>
        <article>
          <strong>Local-first alpha</strong>
          <span>Domain and IP intelligence run through the existing Eye API.</span>
        </article>
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

      <PricingSection />

      <footer className="footer">A product by DrPinnacle</footer>
    </main>
  );
}

function PricingSection() {
  return (
    <section className="pricing-section" aria-labelledby="pricing-heading">
      <div className="pricing-heading">
        <p className="section-kicker">Pricing</p>
        <h2 id="pricing-heading">Choose the intelligence search plan that fits the work.</h2>
      </div>
      <div className="pricing-grid">
        {pricingPlans.map((plan) => (
          <article
            className={`pricing-card ${plan.featured ? "pricing-card-featured" : ""}`}
            key={plan.name}
          >
            <div>
              <h3>{plan.name}</h3>
              <p>{plan.description}</p>
            </div>
            <ul>
              {plan.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
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
  const intelligence = result.intelligence;

  return (
    <div className="results-grid">
      <RiskCard result={result} subject={result.domain} />
      <SummaryCard result={result} title={result.domain} />

      {intelligence ? (
        <Section title="Intelligence Confidence">
          <div className="confidence-panel">
            <div>
              <strong>{intelligence.intelligence_confidence}</strong>
              <span>
                {intelligence.incomplete_intelligence
                  ? "Incomplete Intelligence"
                  : "Source coverage complete"}
              </span>
            </div>
            <ListBlock
              items={intelligence.confidence_notes}
              emptyLabel="No confidence notes returned."
            />
          </div>
        </Section>
      ) : null}

      {intelligence ? (
        <Section title="Email Security">
          <KeyValueData
            data={{
              score: `${intelligence.email_security.score}/100`,
              spf: intelligence.email_security.spf_present ? "Present" : "Missing",
              spf_record: intelligence.email_security.spf_record,
              dmarc: intelligence.email_security.dmarc_present ? "Present" : "Missing",
              dmarc_record: intelligence.email_security.dmarc_record,
              dkim: intelligence.email_security.dkim_status,
            }}
            emptyLabel="No email security posture returned."
          />
          <ListBlock
            items={[
              ...intelligence.email_security.findings,
              ...intelligence.email_security.recommendations,
            ]}
            emptyLabel="No email security findings returned."
          />
        </Section>
      ) : null}

      {intelligence ? (
        <Section title="Web Security Headers">
          <KeyValueData
            data={{
              score: `${intelligence.web_security.score}/100`,
              checked_url: intelligence.web_security.checked_url,
              status_code: intelligence.web_security.status_code,
            }}
            emptyLabel="No web security posture returned."
          />
          <div className="header-list">
            {intelligence.web_security.headers.map((header) => (
              <article className="header-item" key={header.name}>
                <div>
                  <h3>{header.name}</h3>
                  <p>{header.value ?? header.recommendation ?? "No value returned."}</p>
                </div>
                <span className={`status-pill ${header.present ? "status-completed" : "status-failed"}`}>
                  {header.present ? "present" : "missing"}
                </span>
              </article>
            ))}
          </div>
        </Section>
      ) : null}

      {intelligence ? (
        <Section title="TLS">
          {intelligence.tls ? (
            <>
              <KeyValueData
                data={{
                  status: intelligence.tls.status,
                  issuer: intelligence.tls.issuer,
                  subject: intelligence.tls.subject,
                  valid_from: intelligence.tls.valid_from,
                  valid_to: intelligence.tls.valid_to,
                  days_remaining: intelligence.tls.days_remaining,
                }}
                emptyLabel="No TLS certificate data returned."
              />
              <ListBlock
                items={[...intelligence.tls.findings, ...intelligence.tls.recommendations]}
                emptyLabel="No TLS findings returned."
              />
            </>
          ) : (
            <p className="empty-copy">TLS certificate data could not be retrieved.</p>
          )}
        </Section>
      ) : null}

      {intelligence ? (
        <Section title="Recommendations">
          <ListBlock
            items={intelligence.recommendations}
            emptyLabel="No recommendations returned."
          />
        </Section>
      ) : null}

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

      {intelligence ? (
        <Section title="Infrastructure">
          <KeyValueData
            data={{
              server: intelligence.technology.server,
              powered_by: intelligence.technology.powered_by,
              cdn_or_security: intelligence.technology.cdn_or_security,
            }}
            emptyLabel="No technology fingerprint returned."
          />
          <ListBlock
            items={intelligence.technology.findings}
            emptyLabel="No infrastructure findings returned."
          />
        </Section>
      ) : null}
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
        Search a domain or IP address to generate a local{" "}
        {searchType === "domain" ? "Domain" : "IP"} Intelligence report.
      </p>
    </section>
  );
}

function detectSearchType(value: string): SearchType | null {
  const trimmed = value.trim();

  if (isIpAddress(trimmed)) {
    return "ip";
  }

  if (isDomain(trimmed)) {
    return "domain";
  }

  return null;
}

function isIpAddress(value: string) {
  const ipv4Pattern =
    /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
  const ipv6Pattern = /^[0-9a-f:]+$/i;

  return ipv4Pattern.test(value) || (value.includes(":") && ipv6Pattern.test(value));
}

function isDomain(value: string) {
  const domainPattern =
    /^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$/i;

  return domainPattern.test(value);
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
