from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_runs_includes_seeded_controlled_demo_metrics() -> None:
    response = client.get("/api/runs")

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 1

    demo_run = next(run for run in runs if run["id"] == "run-demo-001")
    assert demo_run["name"] == "Controlled demo: dense baseline vs hybrid RAG"
    assert demo_run["metrics"] == {
        "label": "controlled demo metrics",
        "dense_only_recall_at_10": 0.69,
        "hybrid_recall_at_10": 0.84,
        "dense_only_ndcg_at_10": 0.62,
        "hybrid_ndcg_at_10": 0.79,
        "judge_agreement_percent": 84,
        "cache_hit_rate_percent": 40,
        "is_controlled_demo": True,
    }


def test_get_run_returns_results_and_judge_scores() -> None:
    response = client.get("/api/runs/run-demo-001")

    assert response.status_code == 200
    run = response.json()
    assert run["id"] == "run-demo-001"
    assert len(run["results"]) == 3
    assert run["results"][0]["judge_score"]["passed"] is True


def test_get_run_traces_returns_trace_records() -> None:
    response = client.get("/api/runs/run-demo-001/traces")

    assert response.status_code == 200
    traces = response.json()
    assert [trace["stage"] for trace in traces] == ["cache", "retrieval", "judge"]
    assert traces[1]["attributes"]["fusion"] == "rrf"


def test_create_run_returns_created_demo_run() -> None:
    response = client.post("/api/runs", json={"name": "Recruiter walkthrough run"})

    assert response.status_code == 201
    run = response.json()
    assert run["id"].startswith("run-")
    assert run["name"] == "Recruiter walkthrough run"
    assert run["status"] == "completed"
    assert run["metrics"]["label"] == "controlled demo metrics"


def test_get_missing_run_returns_404() -> None:
    response = client.get("/api/runs/run-missing")

    assert response.status_code == 404
