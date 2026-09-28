# Agent de candidature

Agent IA qui analyse une offre d'emploi, la compare à mon profil, et rédige un message
de candidature adapté — en enchaînant lui-même plusieurs outils (function calling),
pas un simple pipeline fixe.

## Pourquoi ce projet

Démontrer un vrai workflow agentique (le modèle décide quels outils appeler et dans
quel ordre), en complément de mes autres projets Data/IA :
- [assistant documentaire RAG](https://github.com/Daoudbamba/docs-ai-assistant) — retrieval, pas d'orchestration d'outils
- [observatoire du chômage](https://github.com/Daoudbamba/chomage-dashboard) — data engineering & dashboard
- [prédiction d'attrition](https://github.com/Daoudbamba/attrition-ml) — machine learning classique

C'est aussi un outil que j'utilise réellement pour ma propre recherche d'alternance.

## Fonctionnement

L'agent dispose de 4 outils et décide lui-même de leur enchaînement :

1. `get_candidate_profile` — lit mon profil (compétences, expériences, projets réels)
2. `match_skills` — compare les compétences demandées par l'offre aux miennes
   (recouvrement de tokens normalisés, pas de LLM — rapide et déterministe)
3. `search_company_info` — recherche best-effort un descriptif de l'entreprise
   (scraping léger, sans clé d'API ; retombe sur une note en cas d'échec)
4. `finalize` — signale la fin du raisonnement et fournit le message de candidature

La boucle (`agent/loop.py`) envoie les messages + outils disponibles au modèle,
exécute les appels d'outils demandés, renvoie les résultats, et recommence jusqu'à
ce que `finalize` soit appelé — avec une limite d'étapes (`MAX_STEPS`) pour éviter
une boucle infinie si le modèle ne conclut jamais.

```
Offre → LLM (choisit un outil) → exécution → résultat → LLM (outil suivant ou finalize)
```

## Lancer le projet

```bash
cp .env.example .env   # renseigner GEMINI_API_KEY
docker compose up --build
```

- Interface : http://localhost:3020
- API : http://localhost:8030/docs

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Les tests sur la boucle de l'agent (`tests/test_loop.py`) simulent les réponses du
modèle (aucun appel réseau réel) pour vérifier : l'enchaînement correct des outils,
le comportement de repli si le modèle répond sans passer par un outil, et la levée
d'une erreur explicite si `MAX_STEPS` est atteint sans `finalize`. Les tests sur
`match_skills` vérifient la logique de correspondance (insensible à la casse et
aux accents, gestion des compétences absentes).

## Limites connues

Le tier gratuit de l'API Gemini est limité (quelques requêtes par minute, 20 par jour
sur le modèle utilisé) — largement suffisant pour une démo mais pas pour un usage
intensif. Le client gère les erreurs transitoires (retry avec backoff) mais pas
l'épuisement du quota journalier, qui nécessite d'attendre le renouvellement.
