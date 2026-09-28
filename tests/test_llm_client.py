import httpx
import pytest
from openai import APIStatusError

from agent.llm_client import call_with_retry


def _status_error(code: int) -> APIStatusError:
    response = httpx.Response(status_code=code, request=httpx.Request("POST", "http://test"))
    return APIStatusError(f"erreur {code}", response=response, body=None)


def test_call_with_retry_succeeds_after_transient_failures(monkeypatch):
    monkeypatch.setattr("agent.llm_client.time.sleep", lambda _: None)
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise _status_error(503)
        return "ok"

    assert call_with_retry(flaky) == "ok"
    assert calls["count"] == 3


def test_call_with_retry_gives_up_on_non_retryable_error():
    def always_fails():
        raise _status_error(400)

    with pytest.raises(APIStatusError) as exc_info:
        call_with_retry(always_fails)
    assert exc_info.value.status_code == 400


def test_call_with_retry_raises_after_max_attempts(monkeypatch):
    monkeypatch.setattr("agent.llm_client.time.sleep", lambda _: None)

    def always_503():
        raise _status_error(503)

    with pytest.raises(APIStatusError):
        call_with_retry(always_503)
