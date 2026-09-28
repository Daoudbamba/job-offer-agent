import os
import time

from openai import APIStatusError, OpenAI

MODEL = os.environ.get("AGENT_MODEL", "gemini-flash-latest")

MAX_RETRIES = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def get_client() -> OpenAI:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY manquant (voir .env.example)")
    return OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


def call_with_retry(fn, *args, **kwargs):
    """Le modèle renvoie régulièrement des 503 (surcharge) en heures de pointe :
    on retente avec un backoff exponentiel avant d'abandonner."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except APIStatusError as exc:
            last_error = exc
            if exc.status_code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES - 1:
                raise
            time.sleep(2**attempt)
    raise last_error
