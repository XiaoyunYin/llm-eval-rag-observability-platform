const serviceCards = [
  {
    title: "Evaluation Backend",
    body: "FastAPI service prepared for baseline vs candidate runs, judge scoring, and provider gateway adapters.",
  },
  {
    title: "Hybrid RAG Layer",
    body: "Planned retrieval path combines dense search, BM25, reciprocal rank fusion, and top-k quality metrics.",
  },
  {
    title: "Observability",
    body: "Trace records are shaped for OpenTelemetry-style events and Elasticsearch-style search in the local demo.",
  },
];

function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">Minimal portfolio implementation</p>
        <h1>LLM Evaluation, RAG & Observability Platform</h1>
        <p className="summary">
          A controlled demo workload for comparing LLM outputs, testing retrieval quality, and
          inspecting trace data with mock providers by default.
        </p>
      </section>

      <section className="architecture" aria-labelledby="architecture-heading">
        <div className="section-heading">
          <p className="eyebrow">Architecture Summary</p>
          <h2 id="architecture-heading">Local full-stack demo scaffold</h2>
        </div>

        <div className="architecture-grid">
          {serviceCards.map((card) => (
            <article className="service-card" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </article>
          ))}
        </div>

        <div className="flow" aria-label="Service flow">
          <span>React Dashboard</span>
          <span>FastAPI API</span>
          <span>PostgreSQL + pgvector</span>
          <span>Redis Cache</span>
          <span>Elasticsearch Traces</span>
        </div>
      </section>
    </main>
  );
}

export default App;
