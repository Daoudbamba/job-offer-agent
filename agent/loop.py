import json
from dataclasses import dataclass, field

from .llm_client import MODEL, call_with_retry, get_client
from .tools import get_candidate_profile, match_skills, search_company_info

MAX_STEPS = 6

SYSTEM_PROMPT = """Tu es un agent qui aide un candidat à analyser une offre d'emploi et à
préparer sa candidature. Suis ces étapes dans l'ordre :
1. Appelle get_candidate_profile pour connaître le profil du candidat.
2. Identifie les compétences demandées dans l'offre, puis appelle match_skills avec cette liste.
3. Si un nom d'entreprise est identifiable dans l'offre, appelle search_company_info.
4. Rédige un court message de candidature (3-4 phrases, en français, ton professionnel et
   direct) qui met en avant les compétences et projets du candidat qui correspondent
   réellement à l'offre — ne jamais inventer une compétence absente du profil.
5. Termine obligatoirement en appelant l'outil finalize avec ce message.

N'invente jamais d'information sur le candidat au-delà de ce que get_candidate_profile renvoie."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_candidate_profile",
            "description": "Renvoie le profil du candidat : compétences, expériences, projets.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "match_skills",
            "description": "Compare une liste de compétences requises par l'offre aux compétences du candidat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "competences_requises": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Compétences/technologies mentionnées dans l'offre.",
                    }
                },
                "required": ["competences_requises"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_info",
            "description": "Recherche un court descriptif public de l'entreprise citée dans l'offre.",
            "parameters": {
                "type": "object",
                "properties": {"nom_entreprise": {"type": "string"}},
                "required": ["nom_entreprise"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finalize",
            "description": "Termine l'analyse et fournit le message de candidature rédigé.",
            "parameters": {
                "type": "object",
                "properties": {
                    "poste": {"type": "string"},
                    "entreprise": {"type": "string"},
                    "message_candidature": {"type": "string"},
                },
                "required": ["message_candidature"],
            },
        },
    },
]

DISPATCH = {
    "get_candidate_profile": lambda **kwargs: get_candidate_profile(),
    "match_skills": lambda **kwargs: match_skills(**kwargs),
    "search_company_info": lambda **kwargs: search_company_info(**kwargs),
}


@dataclass
class AgentResult:
    trace: list = field(default_factory=list)
    poste: str | None = None
    entreprise: str | None = None
    message_candidature: str | None = None
    score_adequation: float | None = None
    competences_correspondantes: list = field(default_factory=list)
    competences_manquantes: list = field(default_factory=list)


class AgentMaxStepsExceeded(RuntimeError):
    def __init__(self, trace: list):
        super().__init__("L'agent n'a pas terminé dans la limite d'étapes autorisée.")
        self.trace = trace


def run_agent(offer_text: str) -> AgentResult:
    client = get_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Voici l'offre d'emploi :\n\n{offer_text}"},
    ]

    result = AgentResult()
    last_match: dict = {}

    for _ in range(MAX_STEPS):
        response = call_with_retry(client.chat.completions.create, model=MODEL, messages=messages, tools=TOOLS)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            # Filet de sécurité : le modèle a répondu sans passer par finalize.
            result.message_candidature = message.content
            result.trace.append({"etape": "reponse_directe", "contenu": message.content})
            return result

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")

            if name == "finalize":
                result.poste = args.get("poste")
                result.entreprise = args.get("entreprise")
                result.message_candidature = args.get("message_candidature")
                result.score_adequation = last_match.get("score_adequation")
                result.competences_correspondantes = last_match.get("competences_correspondantes", [])
                result.competences_manquantes = last_match.get("competences_manquantes", [])
                result.trace.append({"etape": "finalize", "arguments": args})
                return result

            tool_fn = DISPATCH.get(name)
            tool_result = tool_fn(**args) if tool_fn else {"erreur": f"Outil inconnu : {name}"}
            if name == "match_skills":
                last_match = tool_result

            result.trace.append({"etape": name, "arguments": args, "resultat": tool_result})
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_result, ensure_ascii=False)}
            )

    raise AgentMaxStepsExceeded(result.trace)
