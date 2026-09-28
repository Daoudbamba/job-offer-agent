import httpx
from fastapi.testclient import TestClient
from openai import APIStatusError

from agent.loop import AgentMaxStepsExceeded
from api.main import app


def test_health():
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_analyze_rejects_empty_offer():
    client = TestClient(app)
    res = client.post("/api/analyze", json={"offer_text": "   "})
    assert res.status_code == 400


def test_analyze_returns_502_when_llm_provider_fails(monkeypatch):
    def boom(offer_text):
        response = httpx.Response(status_code=429, request=httpx.Request("POST", "http://test"))
        raise APIStatusError("quota dépassée", response=response, body=None)

    monkeypatch.setattr("api.main.run_agent", boom)

    client = TestClient(app)
    res = client.post(
        "/api/analyze", json={"offer_text": "Une offre"}, headers={"Origin": "http://localhost:3020"}
    )

    assert res.status_code == 502
    assert "quota" in res.json()["detail"].lower()
    # Une exception non gérée aurait pu échapper au middleware CORS et apparaître côté
    # navigateur comme un échec réseau opaque plutôt qu'une vraie erreur exploitable.
    assert res.headers.get("access-control-allow-origin") == "*"


def test_analyze_returns_504_when_agent_never_finalizes(monkeypatch):
    def boom(offer_text):
        raise AgentMaxStepsExceeded(trace=[{"etape": "get_candidate_profile"}])

    monkeypatch.setattr("api.main.run_agent", boom)

    client = TestClient(app)
    res = client.post("/api/analyze", json={"offer_text": "Une offre"})

    assert res.status_code == 504
    assert res.json()["detail"]["trace"] == [{"etape": "get_candidate_profile"}]
