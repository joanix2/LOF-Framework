# LOP Framework — Règles de programmation orientée langage

## Architecture

```
Bronze (tickets bruts, append-only)
  → Silver (extraction sémantique spaCy)
  → Reasoning (inférence Datalog)
  → Gold (DSL applicatif)
  → SMT validation (Z3)
  → Compilation (Jinja + patches AST)
  → Projet généré
  → Linters + tests
```

## Sources modifiables

- `definitions/types/` — définitions de types
- `instances/` — instances d'entités
- `templates/` — templates Jinja
- `patches/` — patches AST
- `schemas/` — schémas JSON
- `definitions/targets/` — cibles
- `framework/src/lof/reasoning/profiles/` — règles d'inférence
- `benchmarks/` — scénarios de benchmark
- `tests/` — tests

## Sources interdites

Ne jamais modifier directement :
- `generated/`
- `generated-project/`
- `data/` (sauf via `lof bronze add`)
- `.lof/diagnostics/`
- SDK OpenAPI généré

## Agents

Voir `.opencode/agents/` pour la liste complète et les responsabilités.
L'agent orchestrateur analyse la demande et délègue aux agents spécialisés.

## Skills

Voir `.opencode/skills/` pour les procédures réutilisables.
Chaque skill a un objectif, des étapes, et des validations.

## Workflows

Voir `.opencode/workflows/` pour les enchaînements complets.

## Règles

- Une fonction = une responsabilité
- Pas de logique métier dans les templates Jinja
- Pas de contournement de la validation SMT
- Pas de modification des fichiers générés
- Pas de valeurs métier en dur (utiliser `domain/settings.py`)
- Signatures typées pour toutes les APIs publiques
- `make validate-agentic-system && make format && make lint && make typecheck && make test` après chaque modification
