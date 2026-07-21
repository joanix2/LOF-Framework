# LOP Framework — Règles de programmation orientée langage

## Architecture MDE à 4 niveaux

```
M3  Métacompilateur       src/lof/                     Python
M2  Langage (Profile)     profiles/fastapi-react/      JSON + Jinja
M1  Programme DSL         isoclim.json                 JSON
M0  Application générée   generated-project/           FastAPI + React
```

## Sources modifiables (M2)

- `profiles/fastapi-react/profile.json` — schéma, conventions, contraintes, projections
- `templates/` — templates Jinja
- `src/lof/reasoning/profiles/` — règles d'inférence
- `validation/smt/compilers/` — compilateurs de contraintes
- `benchmarks/` — scénarios de benchmark
- `tests/` — tests

## Sources interdites

- `isoclim.json` et tout programme DSL (M1) — ❌ Jamais, c'est le modèle métier
- `generated-project/` — ❌ Jamais, régénéré à chaque compile
- `.lof/` — ❌ Jamais, interne au compilateur

## Règles

- Pas de logique métier dans les templates Jinja
- Pas de contournement de la validation SMT
- Pas de modification des fichiers générés
- Tout ce qui est M2 doit être dans le profil, pas dans le code Python
- `make format && make lint && make test` après chaque modification

<!-- BEGIN AGENT KANBAN — DO NOT EDIT THIS SECTION -->
## Agent Kanban

Read `.agentkanban/INSTRUCTION.md` for task workflow rules.
Read `.agentkanban/memory.md` for project context.

If a task file (`.agentkanban/tasks/**/*.md`) was referenced earlier in this conversation, re-read it before responding and always respond in and at the end the task file.
<!-- END AGENT KANBAN -->
