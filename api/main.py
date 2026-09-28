from dataclasses import asdict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIStatusError
from pydantic import BaseModel

load_dotenv()

from agent.loop import AgentMaxStepsExceeded, run_agent  # noqa: E402

app = FastAPI(title="Agent d'analyse d'offres d'emploi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class OfferRequest(BaseModel):
    offer_text: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(payload: OfferRequest):
    if not payload.offer_text.strip():
        raise HTTPException(status_code=400, detail="Le texte de l'offre est vide.")
    try:
        result = run_agent(payload.offer_text)
    except AgentMaxStepsExceeded as exc:
        raise HTTPException(
            status_code=504, detail={"message": str(exc), "trace": exc.trace}
        ) from exc
    except APIStatusError as exc:
        # Le modèle (quota, surcharge...) a refusé la requête après les tentatives de
        # relance : on renvoie une erreur explicite plutôt que de laisser fuiter une 500
        # brute que le navigateur affiche comme un échec réseau opaque.
        raise HTTPException(
            status_code=502, detail=f"Le fournisseur LLM a refusé la requête : {exc.message}"
        ) from exc
    return asdict(result)
