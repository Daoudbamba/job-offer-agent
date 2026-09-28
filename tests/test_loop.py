import json
from types import SimpleNamespace

import pytest

from agent.loop import MAX_STEPS, AgentMaxStepsExceeded, run_agent


def _tool_call(call_id: str, name: str, arguments: dict) -> SimpleNamespace:
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=json.dumps(arguments)))


def _message(tool_calls=None, content=None) -> SimpleNamespace:
    msg = SimpleNamespace(tool_calls=tool_calls, content=content)
    msg.model_dump = lambda exclude_none=True: {"role": "assistant", "content": content}
    return msg


def _response(message) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    """Simule client.chat.completions.create en renvoyant une réponse par appel,
    dans l'ordre fourni — permet de tester la boucle sans appeler de vraie API."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        return next(self._responses)


def test_run_agent_happy_path_calls_tools_then_finalizes(monkeypatch):
    responses = [
        _response(_message(tool_calls=[_tool_call("1", "get_candidate_profile", {})])),
        _response(_message(tool_calls=[_tool_call("2", "match_skills", {"competences_requises": ["Python", "Docker"]})])),
        _response(_message(tool_calls=[_tool_call(
            "3", "finalize",
            {"poste": "Data Analyst", "entreprise": "Acme", "message_candidature": "Bonjour,..."},
        )])),
    ]
    monkeypatch.setattr("agent.loop.get_client", lambda: FakeClient(responses))

    result = run_agent("Offre : Data Analyst chez Acme, compétences : Python, Docker")

    assert result.poste == "Data Analyst"
    assert result.entreprise == "Acme"
    assert result.message_candidature == "Bonjour,..."
    assert result.score_adequation == 1.0
    assert [step["etape"] for step in result.trace] == ["get_candidate_profile", "match_skills", "finalize"]


def test_run_agent_raises_when_model_never_finalizes(monkeypatch):
    endless = _response(_message(tool_calls=[_tool_call("x", "get_candidate_profile", {})]))
    monkeypatch.setattr("agent.loop.get_client", lambda: FakeClient([endless] * (MAX_STEPS + 1)))

    with pytest.raises(AgentMaxStepsExceeded) as exc_info:
        run_agent("Une offre quelconque")

    assert len(exc_info.value.trace) == MAX_STEPS


def test_run_agent_falls_back_to_direct_reply_without_tool_calls(monkeypatch):
    direct = _response(_message(tool_calls=None, content="Réponse directe sans outil."))
    monkeypatch.setattr("agent.loop.get_client", lambda: FakeClient([direct]))

    result = run_agent("Une offre quelconque")

    assert result.message_candidature == "Réponse directe sans outil."
