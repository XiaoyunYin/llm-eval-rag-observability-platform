import { useEffect, useMemo, useState, type CSSProperties } from "react";

type ProviderConfig = {
  id: string;
  name: string;
  kind: string;
  model_name: string;
  uses_mock_responses: boolean;
};

type Dataset = {
  id: string;
  name: string;
  version: string;
  case_count: number;
};

type Metrics = {
  label: string;
  dense_only_recall_at_10: number;
  hybrid_recall_at_10: number;
  dense_only_ndcg_at_10: number;
  hybrid_ndcg_at_10: number;
  judge_agreement_percent: number;
  cache_hit_rate_percent: number;
};

type JudgeReview = {
  agreement: boolean;
  status: string;
  judge_a_decision: boolean;
  judge_b_decision: boolean;
};

type EvaluationResult = {
  id: string;
  case_id: string;
  latency_ms: number;
  cache_hit: boolean;
  judge_review: JudgeReview;
};

type EvaluationRun = {
  id: string;
  name: string;
  status: string;
  dataset: Dataset;
  baseline_provider: ProviderConfig;
  candidate_provider: ProviderConfig;
  metrics: Metrics;
  results?: EvaluationResult[];
  created_at: string;
  completed_at: string | null;
};

type TraceRecord = {
  id: string;
  run_id: string;
  case_id: string | null;
  component: string;
  provider: string;
  model: string;
  cache_status: string;
  latency_ms: number;
  token_count: number;
  estimated_cost: number;
  error_type: string | null;
  status: string;
};

type DashboardState = {
  runs: EvaluationRun[];
  selectedRun: EvaluationRun | null;
  traces: TraceRecord[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

const architectureItems = [
  "React dashboard",
  "FastAPI evaluation API",
  "Hybrid RAG retrieval",
  "Provider gateway",
  "Trace records",
  "PostgreSQL/Redis/Elasticsearch via Compose",
];

function App() {
  const [dashboard, setDashboard] = useState<DashboardState>({
    runs: [],
    selectedRun: null,
    traces: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      try {
        setIsLoading(true);
        const runsResponse = await fetch(`${apiBaseUrl}/api/runs`);
        if (!runsResponse.ok) {
          throw new Error(`Run summary request failed with ${runsResponse.status}`);
        }

        const runs = (await runsResponse.json()) as EvaluationRun[];
        const selectedSummary = runs.find((run) => run.id === "run-demo-001") ?? runs[0];
        if (!selectedSummary) {
          throw new Error("No seeded evaluation runs returned by the backend.");
        }

        const [runResponse, tracesResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/api/runs/${selectedSummary.id}`),
          fetch(`${apiBaseUrl}/api/runs/${selectedSummary.id}/traces`),
        ]);

        if (!runResponse.ok) {
          throw new Error(`Run detail request failed with ${runResponse.status}`);
        }
        if (!tracesResponse.ok) {
          throw new Error(`Trace request failed with ${tracesResponse.status}`);
        }

        const selectedRun = (await runResponse.json()) as EvaluationRun;
        const traces = (await tracesResponse.json()) as TraceRecord[];

        if (isMounted) {
          setDashboard({ runs, selectedRun, traces });
          setError(null);
        }
      } catch (caughtError) {
        if (isMounted) {
          setError(caughtError instanceof Error ? caughtError.message : "Unable to load dashboard data.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  const selectedRun = dashboard.selectedRun;
  const metrics = selectedRun?.metrics;
  const results = useMemo(() => selectedRun?.results ?? [], [selectedRun]);

  const cacheRates = useMemo(() => {
    const hitRate = metrics?.cache_hit_rate_percent ?? 0;
    return { hitRate, missRate: Math.max(100 - hitRate, 0) };
  }, [metrics]);

  const manualReviewCount = useMemo(
    () => results.filter((result) => result.judge_review.status === "manual_review").length,
    [results],
  );

  return (
    <main className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Recruiter review dashboard</p>
          <h1>LLM Evaluation, RAG & Observability Platform</h1>
          <p className="summary">
            Full-stack demo for comparing baseline and candidate LLM workflows, measuring retrieval
            quality, and inspecting evaluation traces.
          </p>
        </div>
        <div className="status-panel" aria-label="API status">
          <span className={`status-dot ${error ? "status-dot-error" : ""}`} />
          <span>{error ? "Backend unavailable" : isLoading ? "Loading seeded API" : "Seeded API connected"}</span>
        </div>
      </header>

      {error ? <section className="notice">{error}</section> : null}

      <section className="architecture-band" aria-labelledby="architecture-heading">
        <div className="section-heading">
          <p className="eyebrow">Architecture summary</p>
          <h2 id="architecture-heading">Local evaluation system</h2>
        </div>
        <div className="architecture-flow">
          {architectureItems.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <section className="summary-grid" aria-label="Run summary">
        <MetricCard label="Runs" value={dashboard.runs.length || "—"} detail="Seeded evaluation runs" />
        <MetricCard label="Dataset" value={selectedRun?.dataset.case_count ?? "—"} detail="Evaluation cases" />
        <MetricCard label="Status" value={formatStatus(selectedRun?.status)} detail={selectedRun?.name ?? "Waiting"} />
        <MetricCard label="Provider" value={selectedRun?.candidate_provider.kind ?? "—"} detail="Mock by default" />
      </section>

      <section className="dashboard-grid">
        <div className="panel metrics-panel">
          <div className="panel-heading">
            <p className="eyebrow">Baseline vs candidate</p>
            <h2>Retrieval metrics</h2>
          </div>
          <ComparisonBar
            label="Recall@10"
            baselineLabel="Dense-only"
            candidateLabel="Hybrid RAG"
            baseline={metrics?.dense_only_recall_at_10 ?? 0}
            candidate={metrics?.hybrid_recall_at_10 ?? 0}
          />
          <ComparisonBar
            label="nDCG@10"
            baselineLabel="Dense-only"
            candidateLabel="Hybrid RAG"
            baseline={metrics?.dense_only_ndcg_at_10 ?? 0}
            candidate={metrics?.hybrid_ndcg_at_10 ?? 0}
          />
          <p className="metric-note">{metrics?.label ?? "controlled demo metrics"}</p>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <p className="eyebrow">Judge agreement</p>
            <h2>{metrics ? `${metrics.judge_agreement_percent}%` : "—"}</h2>
          </div>
          <div className="review-list">
            <span>{results.length} judged cases</span>
            <span>{manualReviewCount} manual review</span>
            <span>{results.filter((result) => result.judge_review.agreement).length} agreements</span>
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <p className="eyebrow">Cache behavior</p>
            <h2>{metrics ? `${metrics.cache_hit_rate_percent}% hit rate` : "—"}</h2>
          </div>
          <div className="cache-bars" aria-label="Cache hit and miss rates">
            <div style={{ "--bar-size": cacheRates.hitRate / 20 } as CSSProperties}>
              <span>Hit rate</span>
              <strong>{cacheRates.hitRate}%</strong>
            </div>
            <div style={{ "--bar-size": cacheRates.missRate / 20 } as CSSProperties}>
              <span>Miss rate</span>
              <strong>{cacheRates.missRate}%</strong>
            </div>
          </div>
        </div>

        <div className="panel scope-panel">
          <div className="panel-heading">
            <p className="eyebrow">Limitations and scope</p>
            <h2>Runnable demo version</h2>
          </div>
          <ul>
            <li>Controlled seeded workload, not production traffic.</li>
            <li>Mock providers are used by default.</li>
            <li>PostgreSQL, Redis, and Elasticsearch are local Compose services.</li>
          </ul>
        </div>
      </section>

      <section className="trace-section" aria-labelledby="trace-heading">
        <div className="section-heading">
          <p className="eyebrow">Trace drilldown</p>
          <h2 id="trace-heading">Run component records</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Component</th>
                <th>Case</th>
                <th>Provider</th>
                <th>Model</th>
                <th>Cache</th>
                <th>Latency</th>
                <th>Tokens</th>
                <th>Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dashboard.traces.map((trace) => (
                <tr key={trace.id}>
                  <td>{trace.component}</td>
                  <td>{trace.case_id ?? "run"}</td>
                  <td>{trace.provider}</td>
                  <td>{trace.model}</td>
                  <td>{trace.cache_status}</td>
                  <td>{trace.latency_ms} ms</td>
                  <td>{trace.token_count}</td>
                  <td>${trace.estimated_cost.toFixed(4)}</td>
                  <td>
                    <span className="status-pill">{trace.status}</span>
                  </td>
                </tr>
              ))}
              {!dashboard.traces.length ? (
                <tr>
                  <td colSpan={9}>{isLoading ? "Loading traces..." : "No trace records loaded."}</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function MetricCard({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function ComparisonBar({
  label,
  baselineLabel,
  candidateLabel,
  baseline,
  candidate,
}: {
  label: string;
  baselineLabel: string;
  candidateLabel: string;
  baseline: number;
  candidate: number;
}) {
  return (
    <div className="comparison">
      <div className="comparison-title">
        <h3>{label}</h3>
        <span>{formatDelta(candidate - baseline)}</span>
      </div>
      <ScoreBar label={baselineLabel} value={baseline} variant="baseline" />
      <ScoreBar label={candidateLabel} value={candidate} variant="candidate" />
    </div>
  );
}

function ScoreBar({
  label,
  value,
  variant,
}: {
  label: string;
  value: number;
  variant: "baseline" | "candidate";
}) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <div className="bar-track">
        <div className={`bar-fill ${variant}`} style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <strong>{value.toFixed(2)}</strong>
    </div>
  );
}

function formatDelta(delta: number) {
  const sign = delta >= 0 ? "+" : "";
  return `${sign}${delta.toFixed(2)}`;
}

function formatStatus(status?: string) {
  if (!status) {
    return "—";
  }
  return status.replace(/_/g, " ");
}

export default App;
