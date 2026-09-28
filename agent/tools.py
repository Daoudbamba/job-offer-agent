import json
import re
import unicodedata
from pathlib import Path

import httpx

PROFILE_PATH = Path(__file__).resolve().parent / "profile.json"

STOPWORDS = {
    "de", "des", "du", "la", "le", "les", "un", "une", "et", "en", "avec",
    "pour", "sur", "dans", "a", "au", "aux", "ou", "notions", "avancees",
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9\s]", " ", text)


def _tokens(text: str) -> set[str]:
    return {t for t in _normalize(text).split() if len(t) >= 3 and t not in STOPWORDS}


def get_candidate_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def match_skills(competences_requises: list[str]) -> dict:
    """Compare une liste de compétences requises (texte libre, tel qu'extrait d'une
    offre) aux compétences du candidat, par recouvrement de tokens normalisés."""
    candidate_skills = get_candidate_profile()["competences"]
    candidate_token_map = {skill: _tokens(skill) for skill in candidate_skills}

    matched, missing = [], []
    for required in competences_requises:
        required_tokens = _tokens(required)
        hit = any(required_tokens & candidate_tokens for candidate_tokens in candidate_token_map.values())
        (matched if hit else missing).append(required)

    total = len(competences_requises) or 1
    score = round(len(matched) / total, 2)
    return {"score_adequation": score, "competences_correspondantes": matched, "competences_manquantes": missing}


def search_company_info(nom_entreprise: str, timeout: float = 5.0) -> dict:
    """Recherche best-effort d'un court descriptif de l'entreprise (scraping léger
    de DuckDuckGo, sans clé d'API). En cas d'échec, renvoie une note plutôt que
    de faire échouer l'agent."""
    try:
        response = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": f"{nom_entreprise} entreprise activité"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=timeout,
        )
        response.raise_for_status()
        match = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', response.text, re.DOTALL)
        if not match:
            return {"trouve": False, "resume": "Aucune information trouvée."}
        snippet = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        return {"trouve": True, "resume": snippet[:400]}
    except Exception as exc:  # noqa: BLE001 - outil best-effort, ne doit jamais bloquer l'agent
        return {"trouve": False, "resume": f"Recherche indisponible ({exc.__class__.__name__})."}
